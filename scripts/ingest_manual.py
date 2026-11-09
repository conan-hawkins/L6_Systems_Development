"""Split a Haynes workshop manual PDF into sections and load them into MongoDB.

Run once per manual, offline (not part of the Flask app):

    python scripts/ingest_manual.py "manual.pdf" --vehicle vw_golf_mk2 --dry-run
    python scripts/ingest_manual.py "manual.pdf" --vehicle vw_golf_mk2 --out sections.json
    python scripts/ingest_manual.py "manual.pdf" --vehicle vw_golf_mk2 --mongo

Instead of guessing structure from plain text, it reads the font of every
piece of text (PyMuPDF "dict" output). 

- "Chapter N" titles are 24pt bold.
- Numbered section headings ("12 Hydraulic system - bleeding") are 9.5pt.
- The difficulty rating is a spanner icon drawn with the "Haynes" font,
  where the glyph's text is the digit 1-5.
- Page headers ("Braking system  9•3") are 11pt and larger.

https://pymupdf.readthedocs.io/en/latest/app1.html#dictionary-structure-of-extractdict-and-extractrawdict
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VEHICLES_DIR = PROJECT_ROOT / "helpbot" / "data" / "vehicles"
COLLECTION = "manual_sections"

CHAPTER_RE = re.compile(r"^Chapter\s+(\d+)(?:\s+Part\s+([A-Z]))?:?$")
PAGE_LABEL_RE = re.compile(r"(\d+[A-Z]?\s*•\s*\d+)")


def is_size(span, size, tolerance=0.2):
    return abs(span["size"] - size) <= tolerance


def is_rating_icon(span):
    return span["font"].startswith("Haynes") and span["size"] >= 20


def page_lines(page):
    """Yield each text line on the page as (spans, text, bbox), in reading order.

    Spanner icons are left out here; ratings_on_page() reads them separately.
    """
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans = [s for s in line["spans"] if s["text"].strip() and not is_rating_icon(s)]
            if spans:
                text = " ".join(s["text"].strip() for s in spans)
                yield spans, text, line["bbox"]


def ratings_on_page(page):
    """Return [(x, y, rating)] for every spanner icon on the page."""
    found = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for s in line["spans"]:
                if is_rating_icon(s) and s["text"].strip() in ("1", "2", "3", "4", "5"):
                    found.append((s["bbox"][0], s["bbox"][1], int(s["text"].strip())))
    return found


def page_label_of(page):
    """Return the printed page number, e.g. "9•3", from the 11pt page header."""
    for spans, text, bbox in page_lines(page):
        for s in spans:
            match = PAGE_LABEL_RE.search(s["text"])
            if match and 10.5 <= s["size"] < 12:
                return re.sub(r"\s+", "", match.group(1))
    return None


def nearest_rating(heading_bbox, ratings):
    """Pick the spanner icon level with the heading and just to its right.

    The icon sits at the right-hand edge of the heading's column, so we
    accept anything within ~25pt vertically and ~200pt horizontally.
    This also ignores the 1-5 "Degrees of difficulty" legend, which is
    nowhere near a section heading.
    """
    x0, y0 = heading_bbox[0], heading_bbox[1]
    candidates = [
        (abs(ry - y0), rating)
        for rx, ry, rating in ratings
        if abs(ry - y0) <= 25 and 0 <= rx - x0 <= 200
    ]
    return min(candidates)[1] if candidates else None


def join_lines(lines):
    """Join body lines into paragraphs, re-joining words hyphenated at line ends."""
    text = ""
    for line in lines:
        if text.endswith("-") and line[:1].islower():
            text = text[:-1] + line
        else:
            text = f"{text} {line}" if text else line
    return text


def find_stop_page(doc):
    """Wiring diagrams are images with captions - not useful as text."""
    for _level, title, page in doc.get_toc():
        if title.strip().lower() == "wiring diagrams":
            return page - 1  # get_toc() pages are 1-based
    return doc.page_count


def extract_sections(pdf_path, vehicle_id):
    doc = pymupdf.open(pdf_path)
    stop_page = find_stop_page(doc)

    sections = []
    chapter = None   # {"id": "2A", "title": "..."}
    current = None   # section being filled
    expect_chapter_title = False

    def start_section(number, title, rating, page_label):
        nonlocal current
        current = {
            "_id": f"{vehicle_id}:{chapter['id']}:{number}",
            "vehicle_id": vehicle_id,
            "chapter": chapter["id"],
            "chapter_title": chapter["title"],
            "section": number,
            "title": title,
            "difficulty": rating,
            "pages": [page_label] if page_label else [],
            "lines": [],
        }
        sections.append(current)

    for pno in range(stop_page):
        page = doc[pno]
        ratings = ratings_on_page(page)
        page_label = page_label_of(page)
        if current and page_label and page_label not in current["pages"]:
            current["pages"].append(page_label)
        heading_open = False  # True while a heading wraps onto further lines

        for spans, text, bbox in page_lines(page):
            first = spans[0]

            # Chapter title, e.g. "Chapter 2  Part A:" then "Engine repair ..."
            if is_size(first, 24) and "Bold" in first["font"]:
                match = CHAPTER_RE.match(text)
                if match:
                    chapter = {"id": match.group(1) + (match.group(2) or ""), "title": ""}
                    expect_chapter_title = True
                    current = None
                continue
            if expect_chapter_title and is_size(first, 24):
                chapter["title"] = text
                expect_chapter_title = False
                # Everything before the first numbered section is the
                # chapter's specifications, torque settings and contents.
                start_section(0, f"{chapter['title']} - specifications", None, page_label)
                continue

            if chapter is None:
                continue  # front matter (covered by the vehicle JSON instead)

            # Page headers and chapter tabs; the page label was read above.
            if first["size"] >= 10.5:
                continue

            # Section heading: 9.5pt, starting with a bold section number.
            if is_size(first, 9.5):
                number_text = first["text"].strip()
                if "Bold" in first["font"] and number_text.isdigit():
                    title = " ".join(s["text"].strip() for s in spans[1:])
                    start_section(int(number_text), title,
                                  nearest_rating(bbox, ratings), page_label)
                    heading_open = True
                    continue
                if heading_open and current:
                    current["title"] = f"{current['title']} {text}"
                    continue

            heading_open = False
            if current:
                current["lines"].append(text)

    doc.close()

    for section in sections:
        section["title"] = re.sub(r"\s+", " ", section["title"]).strip()
        section["text"] = join_lines(section.pop("lines"))
    return [s for s in sections if s["text"]]


def save_to_mongo(sections, vehicle_id):
    from dotenv import load_dotenv
    from pymongo import MongoClient, TEXT

    load_dotenv(PROJECT_ROOT / ".env")
    uri = os.environ.get("MONGO_URI")
    if not uri:
        sys.exit("MONGO_URI is not set (see .env.example)")

    client = MongoClient(uri)
    collection = client.get_default_database()[COLLECTION]

    # Replace this vehicle's sections so the script is safe to re-run.
    collection.delete_many({"vehicle_id": vehicle_id})
    collection.insert_many(sections)

    # A collection can only have one text index; weight titles above body text.
    # https://www.mongodb.com/docs/manual/core/indexes/index-types/index-text/
    collection.create_index(
        [("title", TEXT), ("text", TEXT)],
        weights={"title": 10, "text": 1},
        name="manual_text",
    )
    collection.create_index("vehicle_id")
    client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pdf", help="path to the manual PDF")
    parser.add_argument("--vehicle", required=True,
                        help="vehicle id, must match a file in helpbot/data/vehicles/")
    parser.add_argument("--out", help="also write the sections to this JSON file")
    parser.add_argument("--mongo", action="store_true", help="load the sections into MongoDB")
    parser.add_argument("--dry-run", action="store_true", help="print a summary only")
    args = parser.parse_args()

    if not (VEHICLES_DIR / f"{args.vehicle}.json").exists():
        sys.exit(f"No vehicle file {args.vehicle}.json in {VEHICLES_DIR}")

    sections = extract_sections(args.pdf, args.vehicle)

    chapters = sorted({s["chapter"] for s in sections}, key=lambda c: (int(re.match(r"\d+", c).group()), c))
    unrated = [s["_id"] for s in sections if s["section"] and s["difficulty"] is None]
    size_kb = sum(len(s["text"]) for s in sections) / 1024
    print(f"{len(sections)} sections from chapters {', '.join(chapters)} ({size_kb:.0f} KB of text)")
    if unrated:
        # Expected for "General information" style sections, which Haynes doesn't rate.
        print(f"{len(unrated)} sections without a difficulty rating: {', '.join(unrated)}")

    if args.out:
        Path(args.out).write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {args.out}")
    if args.mongo and not args.dry_run:
        save_to_mongo(sections, args.vehicle)
        print(f"Loaded into MongoDB collection '{COLLECTION}'")


if __name__ == "__main__":
    main()

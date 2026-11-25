"""Commands for seeding the database with vehicle reference data."""

import json
from pathlib import Path

import click

from helpbot.extensions import db
from helpbot.models import ServiceSchedule, ScheduleItem, VehicleVariant

DATA_DIR = Path(__file__).parent / "data" / "vehicles"


def schedule_id(family, key):
    """Schedule keys like "pre_aug_1985" repeat across families, so prefix the family."""
    return f"{family}_{key}"


@click.command("seed-vehicles")
def seed_vehicles():
    """Load vehicle reference data from the JSON files into the database."""
    for path in sorted(DATA_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        family = data["id"]

        # "service_schedules" is a dict of {schedule key: [task rows]}, not a list
        for key, items in data["service_schedules"].items():
            # The schedule ID is unique across all families, so we can use it as the primary key.
            sid = schedule_id(family, key)
            schedule = db.session.get(ServiceSchedule, sid)
            if schedule is None:
                schedule = ServiceSchedule(id=sid)
                db.session.add(schedule)
            schedule.family = family
            schedule.name = key

            for row in items:
                # The combination of schedule_id and task is unique, so we can use that to find the existing item.
                item = db.session.scalar(
                    db.select(ScheduleItem).filter_by(schedule_id=sid, task=row["task"])
                )
                if item is None:
                    item = ScheduleItem(schedule_id=sid, task=row["task"])
                    db.session.add(item)
                item.manual_section = row["manual_section"]
                item.mileage_interval = row["miles"]
                item.time_interval_months = row["months"]
                item.only_if_condition = row.get("only_if")

        for v in data["variants"]:
            # The variant ID is unique across all families, so we can use it as the primary key.
            variant = db.session.get(VehicleVariant, v["id"])
            if variant is None:
                variant = VehicleVariant(id=v["id"])
                db.session.add(variant)
            variant.family = family
            variant.name = v["label"]
            variant.schedule_id = schedule_id(family, v["service_schedule"])
            variant.built_from = v["built_from"]
            variant.built_before = v["built_before"]
            variant.engine_cc = v["engine_cc"]
            variant.engine_codes = v["engine_codes"]
            variant.valves = v["valves"]
            variant.oil_capacity_litres = v["oil_capacity_litres"]
            variant.tyre_pressures_cold = v["tyre_pressures_cold"]
            variant.chapters = v["chapters"]
                
    db.session.commit()
    click.echo("Vehicle reference data seeded successfully.")
    
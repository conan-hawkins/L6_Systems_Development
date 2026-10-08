# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

HelpBot is an individual Level 6 coursework project (Systems Development,
COMP6075): a Python web application with SQL and NoSQL databases, cloud
APIs and functions, cloud security, deployment and unit tests, plus a
video demonstration.

## Context files (local only)

`Assignment/` is gitignored and holds the coursework context. Read it
before any planning or design work:

- `Assignment/Assignment.md` - the coursework brief and marking criteria.
- `Assignment/Planning the system Helpbot.md` - the student's system plan
  (scenario, requirements R1-R8, data design, open decisions).

The plan's scenario (car maintenance reminders) is the target. The code
is still the generic help desk scaffold, so check the plan before
assuming a feature exists or is wanted.

## AI use rules (Tier 2)

The brief only allows AI use for:

- generating ideas and structure,
- suggesting improvements to clarity,
- debugging code and identifying errors (acknowledged).

It does not allow AI-generated core content presented as the student's
own work, AI completing the coursework without substantial student
contribution, AI output used without critical review, or unacknowledged
AI use.

When working here:

- Prefer explaining, reviewing, suggesting structure and debugging over
  writing finished feature code.
- If asked to write core application logic, the video script or the
  evaluation, point out the Tier 2 limit before going ahead.
- Credit AI help in every commit with the `Co-authored-by:` trailer
  described in `CONTRIBUTING.md`, and keep the AI use acknowledgement in
  `README.md` up to date.

## Conventions

- Branches, issues, pull requests and commit messages: see
  `CONTRIBUTING.md`.
- Structure: Flask application factory, blueprints in `helpbot/views/`
  and `helpbot/api/`, business logic in `helpbot/services/`, SQL models in
  `helpbot/models/`, MongoDB repositories in `helpbot/nosql/`.

## Commands

```
pip install -e ".[dev]"
flask --app helpbot run --debug
pytest
```

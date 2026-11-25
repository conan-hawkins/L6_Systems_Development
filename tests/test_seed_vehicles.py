"""Tests for the seed-vehicles CLI command."""

from helpbot.extensions import db
from helpbot.models import ScheduleItem, ServiceSchedule, VehicleVariant

EXPECTED = {"schedules": 2, "items": 64, "variants": 5}


# ---------- helpers ----------


def count(model):
    return db.session.scalar(db.select(db.func.count()).select_from(model))


def seed(app):
    result = app.test_cli_runner().invoke(args=["seed-vehicles"])
    assert result.exit_code == 0, result.output
    return result


def counts():
    return {
        "schedules": count(ServiceSchedule),
        "items": count(ScheduleItem),
        "variants": count(VehicleVariant),
    }


# ---------- tests ----------


def test_seed_loads_counts(app):
    seed(app)
    assert counts() == EXPECTED


def test_seed_twice_no_duplicates(app):
    seed(app)
    seed(app)
    assert counts() == EXPECTED


def test_seed_maps_fields(app):
    seed(app)
    variant = db.session.get(VehicleVariant, "vw_golf_mk2_16v")
    assert variant is not None
    assert variant.valves == 16
    assert variant.name
    assert variant.schedule.name == "post_aug_1985"
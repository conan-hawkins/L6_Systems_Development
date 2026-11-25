"""Models for vehicle reference data."""

from helpbot.extensions import db

class ServiceSchedule(db.Model):
    """A service schedule for a vehicle family."""
    __tablename__ = "service_schedules"
   
    id = db.Column(db.String(64), primary_key=True)
    family = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    items = db.relationship("ScheduleItem", back_populates="schedule")


class ScheduleItem(db.Model):
    """A single item in a service schedule."""
    __tablename__ = "schedule_items"
    __table_args__ = (db.UniqueConstraint("schedule_id", "task", name="uq_schedule_task"),)

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.String(64), db.ForeignKey("service_schedules.id"), nullable=False)
    task = db.Column(db.String(255), nullable=False)
    manual_section = db.Column(db.String(64), nullable=True)
    mileage_interval = db.Column(db.Integer, nullable=True)
    time_interval_months = db.Column(db.Integer, nullable=True)
    only_if_condition = db.Column(db.String(64), nullable=True)
    schedule = db.relationship("ServiceSchedule", back_populates="items")
    

class VehicleVariant(db.Model):
    """A specific variant of a vehicle family."""
    __tablename__ = "vehicle_variants"
   
    id = db.Column(db.String(64), primary_key=True)
    family = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    built_from = db.Column(db.String(7), nullable=False)
    built_before = db.Column(db.String(7), nullable=False)
    engine_cc = db.Column(db.JSON, nullable=False)
    engine_codes = db.Column(db.JSON, nullable=False)
    valves = db.Column(db.Integer, nullable=False)
    oil_capacity_litres = db.Column(db.JSON, nullable=False)
    tyre_pressures_cold = db.Column(db.JSON, nullable=False)
    schedule_id = db.Column(db.String(64), db.ForeignKey("service_schedules.id"), nullable=False)
    chapters = db.Column(db.JSON, nullable=False)
    schedule = db.relationship("ServiceSchedule")
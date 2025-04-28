from database import db
from datetime import datetime


class WorkDayEntry(db.Model):
    __tablename__ = 'work_day_entry'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    work_date = db.Column(db.Date, default=datetime.utcnow)
    hours_elapsed = db.Column(db.Float, nullable=False)
    project_name = db.Column(db.String(255), nullable=False)
    project_subpart = db.Column(db.String(255), nullable=False)
    issues = db.Column(db.JSON, default=[])
    is_done = db.Column(db.Boolean, default=False)
    assigned_by = db.Column(db.BigInteger, nullable=False)
    assigned_to = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

from database import db
from datetime import datetime

class WorkEntry(db.Model):
    __tablename__ = 'work_entries'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), nullable=False)  # 🔄 Now stores "EMP-..." instead of Integer
    full_name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    expected_date_of_delivery = db.Column(db.Date, nullable=True)
    work_status = db.Column(db.String(255), nullable=False)
    tasks = db.Column(db.Text, nullable=False)
    issue = db.Column(db.Text, nullable=True)

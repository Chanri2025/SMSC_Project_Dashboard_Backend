from database import db

class AttendanceLog(db.Model):
    __tablename__ = 'attendance_logs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date = db.Column(db.String(20))
    month = db.Column(db.String(20))
    employee_id = db.Column(db.String(50))
    name = db.Column(db.String(100))
    in_time = db.Column(db.String(10))
    out_time = db.Column(db.String(10))
    working_hours = db.Column(db.Float)

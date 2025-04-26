# models/attendance_log.py
from database import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class AttendanceLog(db.Model):
    __tablename__ = 'attendance_logs'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(
        db.String(50),
        ForeignKey('user.employee_id', ondelete='CASCADE'),
        nullable=False
    )
    date = db.Column(db.String(20), nullable=False)
    in_time = db.Column(db.String(10), nullable=True)
    out_time = db.Column(db.String(10), nullable=True)

    # link back up to your User
    user = relationship(
        'User',
        back_populates='attendance_logs',
        uselist=False,
        primaryjoin='AttendanceLog.employee_id==User.employee_id'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'date': self.date,
            'in_time': self.in_time,
            'out_time': self.out_time
        }

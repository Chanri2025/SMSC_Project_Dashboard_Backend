# models/employee.py
from database import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Employee(db.Model):
    __tablename__ = 'employees'

    # same PK as user.id, with a FK to user.id
    id = db.Column(
        db.Integer,
        ForeignKey('user.id', ondelete='CASCADE'),
        primary_key=True
    )
    phone = db.Column(db.String(20), nullable=False)
    work_position = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    profile_photo = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=False)
    fathers_name = db.Column(db.String(120), nullable=False)
    aadhar_no = db.Column(db.String(12), unique=True, nullable=False)

    # back-reference into User
    user = relationship(
        "User",
        back_populates="employee",
        uselist=False
    )

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.user.employee_id,
            'full_name': self.user.full_name,
            'email': self.user.email,
            'phone': self.phone,
            'role': self.user.role,
            'address': self.address,
            'work_position': self.work_position,
            'date_of_birth': self.date_of_birth.strftime('%Y-%m-%d'),
            'fathers_name': self.fathers_name,
            'aadhar_no': self.aadhar_no,
            'profile_photo': self.profile_photo
        }

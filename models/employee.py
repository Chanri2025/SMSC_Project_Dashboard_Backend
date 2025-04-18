from database import db
from datetime import date

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)  # auto-generated numeric ID
    employee_id = db.Column(db.String(50), unique=True, nullable=False)  # <- ✅ custom ID from frontend
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    work_position = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    profile_photo = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=False)
    fathers_name = db.Column(db.String(120), nullable=False)
    aadhar_no = db.Column(db.String(12), unique=True, nullable=False)
    role = db.Column(db.String(50), default='Employee')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,  # ✅ make sure it's returned
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'address': self.address,
            'work_position': self.work_position,
            'date_of_birth': self.date_of_birth.strftime('%Y-%m-%d'),
            'fathers_name': self.fathers_name,
            'aadhar_no': self.aadhar_no,
            'profile_photo': self.profile_photo,
            'password': self.password
        }

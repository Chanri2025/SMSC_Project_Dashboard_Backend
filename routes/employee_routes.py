from flask import Blueprint, request, jsonify
from models.employee import Employee
from models.user import User
from database import db
from datetime import datetime

employee_bp = Blueprint('employee_bp', __name__)


# ✅ Add a new employee
@employee_bp.route('/add', methods=['POST'])
def add_employee():
    try:
        data = request.get_json()

        required_fields = [
            'employee_id', 'full_name', 'email', 'password', 'phone', 'work_position',
            'date_of_birth', 'profile_photo', 'address', 'fathers_name', 'aadhar_no', 'role'
        ]
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400

        if Employee.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        if Employee.query.filter_by(aadhar_no=data['aadhar_no']).first():
            return jsonify({'message': 'Aadhar already exists'}), 400
        if Employee.query.filter_by(employee_id=data['employee_id']).first():
            return jsonify({'message': 'Employee ID already exists'}), 400

        dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()

        # Create User
        new_user = User(
            employee_id=data['employee_id'],
            full_name=data['full_name'],
            email=data['email'],
            password_hash=data['password'],
            role=data['role']
        )
        db.session.add(new_user)
        db.session.flush()

        # Create Employee
        new_emp = Employee(
            id=new_user.id,
            employee_id=data['employee_id'],
            full_name=data['full_name'],
            email=data['email'],
            password=data['password'],
            phone=data['phone'],
            work_position=data['work_position'],
            date_of_birth=dob,
            profile_photo=data['profile_photo'],
            address=data['address'],
            fathers_name=data['fathers_name'],
            aadhar_no=data['aadhar_no'],
            role=data['role']
        )
        db.session.add(new_emp)
        db.session.commit()

        return jsonify({'message': 'Employee added', 'employee_id': new_emp.employee_id}), 201

    except Exception as e:
        return jsonify({'message': 'Error', 'error': str(e)}), 500


# ✅ Get all employees
@employee_bp.route('/all', methods=['GET'])
def get_all_employees():
    employees = Employee.query.all()
    return jsonify([emp.to_dict() for emp in employees])


# ✅ Search employees by name
@employee_bp.route('/search')
def search_employee_by_name():
    name = request.args.get('name')
    results = Employee.query.filter(Employee.full_name.ilike(f"%{name}%")).all()
    return jsonify([emp.to_dict() for emp in results])


# ✅ Get employee by custom employee_id (used throughout the app)
from sqlalchemy import func


@employee_bp.route('/profile', methods=['GET'])
def get_profile_by_employee_id():
    employee_id = request.args.get('employee_id')

    if not employee_id:
        return jsonify({'message': 'Missing employee_id'}), 400

    emp = Employee.query.filter(func.lower(Employee.employee_id) == employee_id.lower()).first()

    if not emp:
        return jsonify({'message': 'Employee not found'}), 404

    return jsonify(emp.to_dict()), 200


# ✅ Update employee by custom employee_id
@employee_bp.route('/profile', methods=['PUT'])
def update_employee_profile():
    data = request.get_json()
    employee_id = data.get('employee_id')

    if not employee_id:
        return jsonify({'message': 'employee_id is missing in request body'}), 400

    emp = Employee.query.filter_by(employee_id=employee_id).first()
    user = User.query.filter_by(employee_id=employee_id).first()

    if not emp or not user:
        return jsonify({'message': 'Employee or User not found'}), 404

    try:
        # ✅ Update Employee table
        emp.full_name = data.get('full_name', emp.full_name)
        emp.email = data.get('email', emp.email)
        emp.phone = data.get('phone', emp.phone)
        emp.work_position = data.get('work_position', emp.work_position)
        emp.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get(
            'date_of_birth') else emp.date_of_birth
        emp.address = data.get('address', emp.address)
        emp.fathers_name = data.get('fathers_name', emp.fathers_name)
        emp.aadhar_no = data.get('aadhar_no', emp.aadhar_no)
        emp.role = data.get('role', emp.role)
        emp.profile_photo = data.get('profile_photo', emp.profile_photo)
        emp.password = data.get('password', emp.password)

        # ✅ Update User table
        user.full_name = emp.full_name
        user.email = emp.email
        user.password_hash = emp.password
        user.role = emp.role

        db.session.commit()
        return jsonify({'message': 'Employee and User updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed', 'error': str(e)}), 500

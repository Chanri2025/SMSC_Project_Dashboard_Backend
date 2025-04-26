# routes/user.py
from flask import Blueprint, request, jsonify
from models.user import User
from models.employee import Employee
from database import db
from datetime import datetime

user_bp = Blueprint('user', __name__)


# ─── CREATE ────────────────────────────────────────────────────────────────
@user_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    # required fields
    req = [
        'employee_id', 'full_name', 'email', 'password',
        'role', 'phone', 'work_position', 'date_of_birth',
        'address', 'fathers_name', 'aadhar_no'
    ]
    missing = [f for f in req if not data.get(f)]
    if missing:
        return jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400

    # uniqueness checks
    if User.query.filter_by(employee_id=data['employee_id']).first():
        return jsonify({'message': 'Employee ID already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    if Employee.query.filter_by(aadhar_no=data['aadhar_no']).first():
        return jsonify({'message': 'Aadhar already exists'}), 400

    # parse DOB
    try:
        dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date_of_birth format, expected YYYY-MM-DD'}), 400

    # build both objects in one go via relationship
    user = User(
        employee_id=data['employee_id'],
        full_name=data['full_name'],
        email=data['email'],
        password_hash=data['password'],
        role=data['role']
    )
    user.employee = Employee(
        phone=data['phone'],
        work_position=data['work_position'],
        date_of_birth=dob,
        profile_photo=data.get('profile_photo'),
        address=data['address'],
        fathers_name=data['fathers_name'],
        aadhar_no=data['aadhar_no']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User (and Employee) created',
        'id': user.id,
        'employee_id': user.employee_id
    }), 201


# ─── LIST ──────────────────────────────────────────────────────────────────
@user_bp.route('/', methods=['GET'])
def list_users():
    users = User.query.order_by(User.id).all()
    out = []
    for u in users:
        e = u.employee
        out.append({
            'id': u.id,
            'employee_id': u.employee_id,
            'full_name': u.full_name,
            'email': u.email,
            'role': u.role,
            'phone': e.phone,
            'work_position': e.work_position,
            'date_of_birth': e.date_of_birth.strftime('%Y-%m-%d'),
            'address': e.address,
            'fathers_name': e.fathers_name,
            'aadhar_no': e.aadhar_no,
            'profile_photo': e.profile_photo
        })
    return jsonify(out), 200


# ─── FETCH ONE ─────────────────────────────────────────────────────────────
@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    u = User.query.get_or_404(user_id)
    e = u.employee  # thanks to the one-to-one
    return jsonify({
        'id': u.id,
        'employee_id': u.employee_id,
        'full_name': u.full_name,
        'email': u.email,
        'role': u.role,
        'phone': e.phone,
        'work_position': e.work_position,
        'date_of_birth': e.date_of_birth.strftime('%Y-%m-%d'),
        'address': e.address,
        'fathers_name': e.fathers_name,
        'aadhar_no': e.aadhar_no,
        'profile_photo': e.profile_photo
    }), 200


# ─── UPDATE ────────────────────────────────────────────────────────────────
@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    u = User.query.get_or_404(user_id)
    e = u.employee

    data = request.get_json() or {}

    # update User fields
    u.full_name = data.get('full_name', u.full_name)
    u.email = data.get('email', u.email)
    u.role = data.get('role', u.role)
    if data.get('password'):
        u.password_hash = data['password']

    # update Employee fields
    if data.get('date_of_birth'):
        try:
            e.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date_of_birth format'}), 400

    e.phone = data.get('phone', e.phone)
    e.work_position = data.get('work_position', e.work_position)
    e.address = data.get('address', e.address)
    e.fathers_name = data.get('fathers_name', e.fathers_name)
    e.aadhar_no = data.get('aadhar_no', e.aadhar_no)
    e.profile_photo = data.get('profile_photo', e.profile_photo)

    db.session.commit()
    return jsonify({'message': 'User and Employee updated successfully'}), 200


# ─── DELETE ────────────────────────────────────────────────────────────────
@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    return jsonify({'message': 'User (and linked Employee) deleted'}), 200


# --- CHANGE PASSWORD -----------------------------------

@user_bp.route('/<int:user_id>/password', methods=['PUT'])
def change_password(user_id):
    """
    Expects JSON: { "new_password": "..." }
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    new_pw = data.get('new_password')
    if not new_pw:
        return jsonify({'message': 'new_password is required'}), 400

    # Directly overwrite the password_hash column
    user.password_hash = new_pw
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'}), 200


# ─── FETCH ONE ─────────────────────────────────────────────────────────────
@user_bp.route('/profile/<string:employee_id>', methods=['GET'])
def get_user_by_employee_id(employee_id):
    """
    Fetch a User (and linked Employee) by their business key `employee_id`.
    """
    u = User.query.filter_by(employee_id=employee_id).first_or_404()
    e = u.employee
    return jsonify({
        'id': u.id,
        'employee_id': u.employee_id,
        'full_name': u.full_name,
        'email': u.email,
        'role': u.role,
        'phone': e.phone,
        'work_position': e.work_position,
        'date_of_birth': e.date_of_birth.strftime('%Y-%m-%d'),
        'address': e.address,
        'fathers_name': e.fathers_name,
        'aadhar_no': e.aadhar_no,
        'profile_photo': e.profile_photo
    }), 200

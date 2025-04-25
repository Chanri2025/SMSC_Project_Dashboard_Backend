# routes/auth.py
from flask import Blueprint, request, jsonify
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or user.password_hash != password:
        return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({
        'message': 'Login successful',
        'id': user.id,  # ← include the PK here
        'employee_id': user.employee_id,
        'full_name': user.full_name,
        'email': user.email,
        'role': user.role
    }), 200

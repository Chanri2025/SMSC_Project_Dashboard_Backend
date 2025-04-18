from flask import Blueprint, request, jsonify
from models.user import User
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # ✅ Debug print to verify input
    print("Received password:", data['password'])
    print("Stored password:", user.password_hash)

    if user.password_hash == data['password']:  # Plaintext match (for dev only)
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'employee_id': user.employee_id,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role
        }), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401
    
from flask import Blueprint, request, jsonify
from models.user import User
from services.auth_service import hash_password, verify_password
from database import db

auth_bp = Blueprint('auth', __name__)

# Register a new user
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if email already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'Email already registered'}), 400

    new_user = User(
        full_name=data['full_name'],
        email=data['email'],
        password_hash=hash_password(data['password'])  # Store hashed password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201

# Login a user
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and verify_password(user.password_hash, data['password']):
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'full_name': user.full_name,
            'email': user.email
        })
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Get user profile
@auth_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'user_id': user.id,
        'full_name': user.full_name,
        'email': user.email
    })

# Update user profile
@auth_bp.route('/profile/update/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()

    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'Email already in use'}), 400
        user.email = data['email']

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

# Change password
@auth_bp.route('/profile/change-password/<int:user_id>', methods=['PUT'])
def change_password(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()

    if not verify_password(user.password_hash, data['old_password']):
        return jsonify({'message': 'Old password is incorrect'}), 401

    user.password_hash = hash_password(data['new_password'])
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'})

# Delete user account
@auth_bp.route('/profile/delete/<int:user_id>', methods=['DELETE'])
def delete_account(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Account deleted successfully'})

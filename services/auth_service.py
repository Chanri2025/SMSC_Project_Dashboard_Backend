from werkzeug.security import generate_password_hash, check_password_hash

# Function to hash a password before storing it
def hash_password(password):
    return generate_password_hash(password)

# Function to verify password during login
def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

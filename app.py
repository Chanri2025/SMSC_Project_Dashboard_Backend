from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import Config
from database import db

# Blueprints
from routes.employee_routes import employee_bp
from routes.auth import auth_bp
from routes.work_entry_routes import work_entry_bp
from routes.attendance_route import attendance_bp  # ✅ FIXED: corrected file name

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)

# ✅ CORS updated to allow React frontend access
CORS(app, supports_credentials=True, resources={
    r"/*": {"origins": ["http://localhost:3002", "http://localhost:3001"]}
})

# Register blueprints
app.register_blueprint(employee_bp, url_prefix='/employees')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(work_entry_bp, url_prefix='/work')
app.register_blueprint(attendance_bp, url_prefix='/attendance')  # ✅ Added successfully

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

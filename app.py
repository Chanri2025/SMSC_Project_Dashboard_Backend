from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import Config
from database import db

# Blueprints
from routes.auth import auth_bp
from routes.work_entry_routes import work_entry_bp
from routes.attendance_route import attendance_bp
from routes.user_routes import user_bp

app = Flask(__name__)
# ✅ CORS updated to allow React frontend access
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow CORS for all routes
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(work_entry_bp, url_prefix='/work')
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(user_bp, url_prefix='/users')


@app.route("/")
def home():
    return "SMSC API is running!"


# Run the app
if __name__ == '__main__':
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

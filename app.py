from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS  # ✅ Import CORS
from config import Config
from database import db
from routes.auth import auth_bp
from routes.project_routes import project_bp
from routes.user_routes import user_bp

app = Flask(__name__)
app.config.from_object(Config)

# ✅ Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ✅ Enable CORS for all routes
CORS(app)  # This allows all origins by default

# ✅ Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(project_bp, url_prefix='/projects')

if __name__ == '__main__':
    app.run(debug=True)

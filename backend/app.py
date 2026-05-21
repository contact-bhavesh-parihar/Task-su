from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import os

from config import Config
from model import db
from routes.auth import auth_bp
from routes.project import projects_bp
from routes.task import tasks_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)

app.config.from_object(Config)

print("DATABASE URL:", app.config.get("SQLALCHEMY_DATABASE_URI"))

db.init_app(app)

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

@app.route("/")
def home():
    return "Backend Running Successfully"

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(projects_bp, url_prefix="/projects")
app.register_blueprint(tasks_bp, url_prefix="/tasks")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

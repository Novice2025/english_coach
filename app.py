import os
from flask import Flask
from database.db import db
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.main import main_bp
from flask_login import LoginManager
from models.user import User

def create_app():
    app = Flask(__name__)
    
    # SECURITY: Use an environment variable for the secret key, or a fallback for local dev
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-placeholder-123')
    
    # DATABASE: Use PostgreSQL if available (on Render), otherwise use SQLite
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///english_coach.db'
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    with app.app_context(): db.create_all()    with app.app_context(): db.create_all()
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    # SERVERS: They often tell the app which port to use via an environment variable
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

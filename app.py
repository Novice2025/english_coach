from flask import Flask
from database.db import db
from routes.auth import auth_bp
from routes.main import main_bp
from flask_login import LoginManager
from models.user import User
import os

def create_app():
    app = Flask(__name__)
    
    # Security Key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_123')
    
    # Absolute Database Path
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'english_coach.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registering the maps to your pages
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

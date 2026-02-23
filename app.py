from flask import Flask
from database.db import db
from routes.auth import auth_bp
from flask_login import LoginManager
from models.user import User
import os

def create_app():
    app = Flask(__name__)
    
    # Use an environment variable for the secret key or a default for now
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_123')
    
    # Path for Render's writable directory
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '/opt/render/project/src/english_coach.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)

    # This creates the database tables automatically on Render
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

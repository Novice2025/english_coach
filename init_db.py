from app import create_app, db
from models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    print("Building database tables...")
    db.create_all()
    
    # Create Admin if it doesn't exist
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("Creating admin account...")
        new_admin = User(
            name="Admin User",
            email="admin@test.com",
            password_hash=generate_password_hash("password123"),
            role="admin"
        )
        db.session.add(new_admin)
        db.session.commit()
        print("--- SUCCESS: Admin created (admin@test.com / password123) ---")
    else:
        print("--- SUCCESS: Database is ready! ---")

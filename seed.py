import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from app import create_app
from database.db import db
from models.user import User
from models.course import Course
from models.module import Module
from models.lesson import Lesson

def seed_data():
    app = create_app()
    with app.app_context():
        print("Cleaning up old data...")
        db.drop_all()
        db.create_all()

        # 2. Create Admin and Student Users 
        # Matches your model: 'name' instead of 'username', 'password_hash' instead of 'password'
        print("Creating users...")
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            last_login=datetime.now(timezone.utc)
        )
        student = User(
            name="John Student",
            email="student@example.com",
            password_hash=generate_password_hash("student123"),
            role="student",
            last_login=datetime.now(timezone.utc)
        )
        db.session.add_all([admin, student])

        # 3. Create a Sample Course (Meeting Survival)
        print("Creating sample course...")
        course = Course(
            title="Meeting Survival",
            description="Essential English for professional meetings.",
            price=49.99,
            is_published=True
        )
        db.session.add(course)
        db.session.flush() 

        # 4. Create Modules
        mod1 = Module(title="Before the meeting", order_index=1, course_id=course.id)
        db.session.add(mod1)
        db.session.flush()

        # 5. Create Lessons
        # Video Lesson
        lesson1 = Lesson(
            title="Attend a meeting",
            content_type="video",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            order_index=1,
            is_published=True,
            module_id=mod1.id
        )

        # PDF Lesson
        lesson2 = Lesson(
            title="Meeting Vocabulary PDF",
            content_type="pdf",
            pdf_file="uploads/pdfs/sample.pdf", 
            order_index=2,
            is_published=True,
            module_id=mod1.id
        )

        db.session.add_all([lesson1, lesson2])
        db.session.commit()
        
        print("--- SEED COMPLETE ---")
        print("Login with: admin@example.com / admin123")

if __name__ == "__main__":
    seed_data()
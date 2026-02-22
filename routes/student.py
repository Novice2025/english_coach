import io
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors

from database.db import db
from models.course import Course
from models.module import Module
from models.lesson import Lesson
from models.progress import Progress
from models.user import User
from models.quiz import Quiz  # Ensure this is imported
from models.message import Message # For the Support System

student_bp = Blueprint('student', __name__)

# --- DASHBOARD & PROFILE ---

@student_bp.route('/my-courses')
@login_required
def my_courses():
    courses = Course.query.filter_by(is_published=True).all()
    for course in courses:
        total_lessons = Lesson.query.join(Module).filter(Module.course_id == course.id).count()
        if total_lessons > 0:
            completed_count = Progress.query.join(Lesson).join(Module)\
                .filter(Module.course_id == course.id, Progress.user_id == current_user.id).count()
            course.progress_percent = int((completed_count / total_lessons) * 100)
        else:
            course.progress_percent = 0

    milestone_reached = (current_user.xp_points > 0 and current_user.xp_points % 100 == 0)
    return render_template('student/dashboard.html', 
                           courses=courses, 
                           milestone_reached=milestone_reached)

@student_bp.route('/profile')
@login_required
def profile():
    total_mins = db.session.query(db.func.sum(Lesson.duration_minutes))\
        .join(Progress, Lesson.id == Progress.lesson_id)\
        .filter(Progress.user_id == current_user.id).scalar() or 0
    
    hours = total_mins // 60
    mins = total_mins % 60
    watch_time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

    badges = []
    if current_user.xp_points >= 10:
        badges.append({"name": "First Step", "icon": "👣", "desc": "Completed your first lesson"})
    if current_user.xp_points >= 500:
        badges.append({"name": "Dedicated", "icon": "📚", "desc": "Earned 500 XP Points"})
    if current_user.streak_days >= 7:
        badges.append({"name": "Consistency King", "icon": "🔥", "desc": "7-Day Login Streak"})

    return render_template('student/profile.html', watch_time=watch_time_str, badges=badges)

# --- LEARNING & PLAYER ---

@student_bp.route('/course/<int:course_id>/lesson/<int:lesson_id>')
@login_required
def watch_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order_index).all()
    
    progress_record = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
    is_completed = progress_record is not None
    
    return render_template('student/player.html', 
                           course=course, 
                           lesson=lesson, 
                           modules=modules,
                           is_completed=is_completed)

@student_bp.route('/lesson/<int:lesson_id>/toggle-complete', methods=['POST'])
@login_required
def toggle_complete(lesson_id):
    course_id = request.form.get('course_id')
    existing_progress = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    
    if existing_progress:
        db.session.delete(existing_progress)
        current_user.xp_points = max(0, current_user.xp_points - 10)
        flash("Lesson marked as incomplete.", "info")
    else:
        new_progress = Progress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(new_progress)
        current_user.xp_points += 10
        flash("Lesson completed! +10 XP earned 🎉", "success")
        
    db.session.commit()
    return redirect(url_for('student.watch_lesson', course_id=course_id, lesson_id=lesson_id))

# --- QUIZ LOGIC ---

@student_bp.route('/module/<int:module_id>/quiz')
@login_required
def take_quiz(module_id):
    module = Module.query.get_or_404(module_id)
    quizzes = Quiz.query.filter_by(module_id=module_id).all()
    
    if not quizzes:
        flash("No quiz available for this module yet.", "info")
        return redirect(request.referrer)
        
    return render_template('student/quiz.html', module=module, quizzes=quizzes)

@student_bp.route('/quiz/<int:module_id>/submit', methods=['POST'])
@login_required
def submit_quiz(module_id):
    quizzes = Quiz.query.filter_by(module_id=module_id).all()
    correct_count = 0
    total_xp = 0

    for quiz in quizzes:
        selected = request.form.get(f'quiz_{quiz.id}')
        if selected == quiz.correct_answer:
            correct_count += 1
            total_xp += quiz.xp_reward

    score = int((correct_count / len(quizzes)) * 100) if quizzes else 0
    
    if score >= 80:
        current_user.xp_points += total_xp
        db.session.commit()
        flash(f"Quiz passed! You earned {total_xp} XP!", "success")
    else:
        flash("Quiz failed. You need 80% to earn XP. Try again!", "error")

    return render_template('student/quiz_result.html', score=score, xp_earned=total_xp if score >= 80 else 0)

# --- SUPPORT SYSTEM ---

@student_bp.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    if request.method == 'POST':
        new_msg = Message(
            user_id=current_user.id,
            subject=request.form.get('subject'),
            body=request.form.get('body')
        )
        db.session.add(new_msg)
        db.session.commit()
        flash("Message sent to Coach Vishul!", "success")
        return redirect(url_for('student.support'))
    return render_template('student/support.html')

# --- LEADERBOARD & CERTIFICATES ---

@student_bp.route('/leaderboard')
@login_required
def leaderboard():
    students = User.query.filter_by(role='student').order_by(User.xp_points.desc()).limit(10).all()
    return render_template('student/leaderboard.html', students=students)

@student_bp.route('/course/<int:course_id>/certificate')
@login_required
def download_certificate(course_id):
    course = Course.query.get_or_404(course_id)
    total_lessons = Lesson.query.join(Module).filter(Module.course_id == course.id).count()
    completed_count = Progress.query.join(Lesson).join(Module)\
        .filter(Module.course_id == course.id, Progress.user_id == current_user.id).count()
    
    if total_lessons == 0 or completed_count < total_lessons:
        flash("Course not 100% complete.", "error")
        return redirect(url_for('student.my_courses'))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    p.setStrokeColor(colors.HexColor('#4f46e5'))
    p.setLineWidth(12)
    p.rect(40, 40, width-80, height-80)
    
    p.setFont("Helvetica-Bold", 45)
    p.drawCentredString(width/2, height - 180, "CERTIFICATE OF COMPLETION")
    p.setFont("Helvetica-BoldOblique", 35)
    p.drawCentredString(width/2, height - 300, current_user.name.upper())
    p.setFont("Helvetica-Bold", 28)
    p.drawCentredString(width/2, height - 400, course.title)
    
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, 80, f"Issued on {datetime.now().strftime('%Y-%m-%d')} | Vishul English Coach")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, 
                     download_name=f"Certificate_{course.title.replace(' ', '_')}.pdf", 
                     mimetype='application/pdf')
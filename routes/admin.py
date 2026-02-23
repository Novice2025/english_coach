from models.user import User, course, module, lesson
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps
from database.db import db
from models.user import User, course, module, lesson
from models.course import course
from models.module import module
from models.lesson import lesson

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- DASHBOARD & COURSES ---
@admin_bp.route('/')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/courses')
@admin_required
def manage_courses():
    courses = course.query.all()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/course/new', methods=['GET', 'POST'])
@admin_required
def new_course():
    if request.method == 'POST':
        course = course(
            title=request.form.get('title'),
            description=request.form.get('description'),
            instructor_name=request.form.get('instructor_name'),
            price=float(request.form.get('price', 0))
        )
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('admin.manage_courses'))
    return render_template('admin/course_form.html')

@admin_bp.route('/course/edit/<int:course_id>', methods=['GET', 'POST'])
@admin_required
def edit_course(course_id):
    course = course.query.get_or_404(course_id)
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.description = request.form.get('description')
        course.instructor_name = request.form.get('instructor_name')
        course.price = float(request.form.get('price', 0))
        db.session.commit()
        return redirect(url_for('admin.manage_courses'))
    return render_template('admin/course_form.html', course=course)

@admin_bp.route('/course/delete/<int:course_id>', methods=['POST'])
@admin_required
def delete_course(course_id):
    course = course.query.get_or_404(course_id)
    for module in course.modules:
        lesson.query.filter_by(module_id=module.id).delete()
    module.query.filter_by(course_id=course_id).delete()
    db.session.delete(course)
    db.session.commit()
    flash('course deleted!', 'success')
    return redirect(url_for('admin.manage_courses'))

# --- MODULES ---
@admin_bp.route('/course/<int:course_id>/modules')
@admin_required
def manage_modules(course_id):
    course = course.query.get_or_404(course_id)
    modules = module.query.filter_by(course_id=course_id).order_by(module.order_index).all()
    return render_template('admin/modules.html', course=course, modules=modules)

@admin_bp.route('/course/<int:course_id>/module/add', methods=['GET', 'POST'])
@admin_required
def add_module(course_id):
    course = course.query.get_or_404(course_id)
    if request.method == 'POST':
        new_module = module(
            course_id=course_id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            order_index=request.form.get('order_index', 0)
        )
        db.session.add(new_module)
        db.session.commit()
        return redirect(url_for('admin.manage_modules', course_id=course_id))
    return render_template('admin/module_form.html', course_id=course_id, course=course)

@admin_bp.route('/module/edit/<int:module_id>', methods=['GET', 'POST'])
@admin_required
def edit_module(module_id):
    module = module.query.get_or_404(module_id)
    if request.method == 'POST':
        module.title = request.form.get('title')
        module.description = request.form.get('description')
        module.order_index = request.form.get('order_index', 0)
        db.session.commit()
        return redirect(url_for('admin.manage_modules', course_id=module.course_id))
    return render_template('admin/module_form.html', module=module, course_id=module.course_id)

# --- LESSONS ---
@admin_bp.route('/module/<int:module_id>/lessons')
@admin_required
def manage_lessons(module_id):
    module = module.query.get_or_404(module_id)
    lessons = lesson.query.filter_by(module_id=module_id).order_by(lesson.order_index).all()
    return render_template('admin/lessons.html', module=module, lessons=lessons)

@admin_bp.route('/module/<int:module_id>/lesson/add', methods=['GET', 'POST'])
@admin_required
def add_lesson(module_id):
    module = module.query.get_or_404(module_id)
    if request.method == 'POST':
        file = request.files.get('lesson_file')
        video_url = request.form.get('video_url')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            video_url = filename
        
        lesson = lesson(
            module_id=module_id,
            title=request.form.get('title'),
            content_type=request.form.get('content_type'),
            video_url=video_url,
            description=request.form.get('description'),
            order_index=request.form.get('order_index', 0)
        )
        db.session.add(lesson)
        db.session.commit()
        return redirect(url_for('admin.manage_lessons', module_id=module_id))
    return render_template('admin/lesson_form.html', module=module)

@admin_bp.route('/lesson/edit/<int:lesson_id>', methods=['GET', 'POST'])
@admin_required
def edit_lesson(lesson_id):
    lesson = lesson.query.get_or_404(lesson_id)
    module = module.query.get(lesson.module_id)
    if request.method == 'POST':
        lesson.title = request.form.get('title')
        lesson.content_type = request.form.get('content_type')
        lesson.video_url = request.form.get('video_url')
        lesson.description = request.form.get('description')
        lesson.order_index = request.form.get('order_index', 0)
        db.session.commit()
        return redirect(url_for('admin.manage_lessons', module_id=lesson.module_id))
    return render_template('admin/lesson_form.html', lesson=lesson, module=module)

@admin_bp.route('/lesson/delete/<int:lesson_id>', methods=['POST'])
@admin_required
def delete_lesson(lesson_id):
    lesson = lesson.query.get_or_404(lesson_id)
    mid = lesson.module_id
    db.session.delete(lesson)
    db.session.commit()
    return redirect(url_for('admin.manage_lessons', module_id=mid))

from flask import Blueprint, render_template
from models.course import Course

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch ALL courses so the student can see them in the catalog
    all_courses = Course.query.all()
    return render_template('index.html', courses=all_courses)

@main_bp.route('/dashboard')
def dashboard():
    # For now, showing all, later we will show only purchased
    my_courses = Course.query.all()
    return render_template('dashboard.html', courses=my_courses)

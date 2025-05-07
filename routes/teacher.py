from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import Class, Attendee

bp = Blueprint('teacher', __name__)

@bp.route('/teacher/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher_dashboard.html', classes=classes)

@bp.route('/teacher/mark_attendance/<int:class_id>', methods=['POST'])
@login_required
def mark_attendance(class_id):
    if current_user.role != 'teacher':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    attendee_id = request.form['attendee_id']
    attendee = Attendee.query.get(attendee_id)
    if attendee:
        attendee.checked_in = True
        db.session.commit()
        flash('Attendance marked')
    return redirect(url_for('teacher.dashboard'))
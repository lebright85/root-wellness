from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Class, Attendee
from extensions import db

bp = Blueprint('teacher', __name__)

@bp.route('/teacher/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        flash('Access denied: Teachers only.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get classes taught by the current teacher
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    return render_template('dashboard_teacher.html', classes=classes)

@bp.route('/teacher/check_in/<int:attendee_id>', methods=['POST'])
@login_required
def check_in(attendee_id):
    if current_user.role != 'teacher':
        flash('Access denied: Teachers only.', 'danger')
        return redirect(url_for('auth.login'))
    
    attendee = Attendee.query.get_or_404(attendee_id)
    # Verify the attendee belongs to a class taught by the current teacher
    if attendee.class_ref.teacher_id != current_user.id:
        flash('Access denied: Not your attendee.', 'danger')
        return redirect(url_for('teacher.dashboard'))
    
    # Toggle check-in status
    attendee.checked_in = not attendee.checked_in
    db.session.commit()
    flash(f'Attendee {attendee.name} check-in status updated.', 'success')
    return redirect(url_for('teacher.dashboard'))
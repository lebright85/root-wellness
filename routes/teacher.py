from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Class, Attendee
from extensions import db
from datetime import datetime, time, date

bp = Blueprint('teacher', __name__)

@bp.route('/teacher/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role != 'teacher':
        flash('Access denied: Teachers only.', 'danger')
        return redirect(url_for('auth.login'))
    
    today = date.today()
    today_classes = Class.query.filter_by(teacher_id=current_user.id).filter(Class.date == today).all()
    
    if request.method == 'POST':
        # Set Time In
        if 'set_time_in' in request.form:
            try:
                attendee_id = int(request.form['attendee_id'])
                time_in_str = request.form['time_in']
                attendee = Attendee.query.get_or_404(attendee_id)
                
                # Verify attendee belongs to teacher's class
                if attendee.class_.teacher_id != current_user.id:
                    flash('Access denied: Not your attendee.', 'danger')
                    return redirect(url_for('teacher.dashboard'))
                
                if time_in_str:
                    attendee.time_in = datetime.strptime(time_in_str, '%H:%M').time()
                    attendee.checked_in = True
                    db.session.commit()
                    flash(f'{attendee.name} time in set successfully.', 'success')
                else:
                    flash('Please provide a valid time.', 'danger')
            except ValueError as e:
                flash(f'Error setting time in: {str(e)}', 'danger')
        
        # Set Time Out
        elif 'set_time_out' in request.form:
            try:
                attendee_id = int(request.form['attendee_id'])
                time_out_str = request.form['time_out']
                attendee = Attendee.query.get_or_404(attendee_id)
                
                # Verify attendee belongs to teacher's class
                if attendee.class_.teacher_id != current_user.id:
                    flash('Access denied: Not your attendee.', 'danger')
                    return redirect(url_for('teacher.dashboard'))
                
                if time_out_str:
                    attendee.time_out = datetime.strptime(time_out_str, '%H:%M').time()
                    attendee.checked_in = False
                    db.session.commit()
                    flash(f'{attendee.name} time out set successfully.', 'success')
                else:
                    flash('Please provide a valid time.', 'danger')
            except ValueError as e:
                flash(f'Error setting time out: {str(e)}', 'danger')
        
        # Save Comment
        elif 'save_comment' in request.form:
            try:
                attendee_id = int(request.form['attendee_id'])
                comment = request.form['comment'] or None
                attendee = Attendee.query.get_or_404(attendee_id)
                
                # Verify attendee belongs to teacher's class
                if attendee.class_.teacher_id != current_user.id:
                    flash('Access denied: Not your attendee.', 'danger')
                    return redirect(url_for('teacher.dashboard'))
                
                attendee.comments = comment
                db.session.commit()
                flash(f'Comment for {attendee.name} saved successfully.', 'success')
            except ValueError as e:
                flash(f'Error saving comment: {str(e)}', 'danger')
        
        return redirect(url_for('teacher.dashboard'))
    
    return render_template('teacher_dashboard.html', 
                         today_classes=today_classes, 
                         today=today)
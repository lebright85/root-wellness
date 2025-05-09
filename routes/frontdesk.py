from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Class, Attendee, User
from extensions import db
from datetime import datetime, time, date

bp = Blueprint('frontdesk', __name__)

@bp.route('/frontdesk/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role != 'frontdesk':
        flash('Access denied: Front Desk only.', 'danger')
        return redirect(url_for('auth.login'))
    
    classes = Class.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    today = date.today()
    today_classes = Class.query.filter(Class.date == today).all()
    total_classes = len(classes)
    total_attendees = Attendee.query.count()
    checked_in_attendees = Attendee.query.filter_by(checked_in=True).count()
    
    if request.method == 'POST':
        # Check In Attendee
        if 'check_in' in request.form:
            try:
                attendee_id = int(request.form['attendee_id'])
                attendee = Attendee.query.get_or_404(attendee_id)
                attendee.checked_in = True
                attendee.time_in = datetime.now().time()
                db.session.commit()
                flash(f'{attendee.name} checked in successfully.', 'success')
            except ValueError as e:
                flash(f'Error checking in attendee: {str(e)}', 'danger')
        
        # Check Out Attendee
        elif 'check_out' in request.form:
            try:
                attendee_id = int(request.form['attendee_id'])
                attendee = Attendee.query.get_or_404(attendee_id)
                attendee.checked_in = False
                attendee.time_out = datetime.now().time()
                db.session.commit()
                flash(f'{attendee.name} checked out successfully.', 'success')
            except ValueError as e:
                flash(f'Error checking out attendee: {str(e)}', 'danger')
        
        return redirect(url_for('frontdesk.dashboard'))
    
    return render_template('frontdesk_dashboard.html', 
                         classes=classes, 
                         teachers=teachers, 
                         today_classes=today_classes, 
                         today=today,
                         total_classes=total_classes,
                         total_attendees=total_attendees,
                         checked_in_attendees=checked_in_attendees)

@bp.route('/frontdesk/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if current_user.role != 'frontdesk':
        flash('Access denied: Front Desk only.', 'danger')
        return redirect(url_for('auth.login'))
    
    classes = Class.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    
    if request.method == 'POST':
        # Add Class
        if 'add_class' in request.form:
            try:
                class_name = request.form['class_name']
                class_date = datetime.strptime(request.form['class_date'], '%Y-%m-%d').date()
                class_time = datetime.strptime(request.form['class_time'], '%H:%M').time()
                teacher_id = int(request.form['teacher_id'])
                location = request.form['location']
                
                new_class = Class(
                    name=class_name,
                    date=class_date,
                    time=class_time,
                    teacher_id=teacher_id,
                    location=location
                )
                db.session.add(new_class)
                db.session.commit()
                flash('Class added successfully.', 'success')
            except ValueError as e:
                flash(f'Error adding class: {str(e)}', 'danger')
        
        # Add Attendee
        elif 'add_attendee' in request.form:
            try:
                attendee_name = request.form['attendee_name']
                class_id = int(request.form['class_id'])
                stipend = 'stipend' in request.form
                group = request.form['group'] or None
                group_hour = request.form['group_hour'] or None
                group_type = request.form['group_type'] or None
                time_in = datetime.strptime(request.form['time_in'], '%H:%M').time() if request.form['time_in'] else None
                time_out = datetime.strptime(request.form['time_out'], '%H:%M').time() if request.form['time_out'] else None
                comments = request.form['comments'] or None
                
                new_attendee = Attendee(
                    name=attendee_name,
                    class_id=class_id,
                    stipend=stipend,
                    group=group,
                    group_hour=group_hour,
                    group_type=group_type,
                    time_in=time_in,
                    time_out=time_out,
                    comments=comments,
                    checked_in=False
                )
                db.session.add(new_attendee)
                db.session.commit()
                flash('Attendee added successfully.', 'success')
            except ValueError as e:
                flash(f'Error adding attendee: {str(e)}', 'danger')
        
        return redirect(url_for('frontdesk.manage'))
    
    return render_template('frontdesk_manage.html', 
                         classes=classes, 
                         teachers=teachers)
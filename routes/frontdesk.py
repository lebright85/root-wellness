from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import Class, User, Attendee
from datetime import datetime

bp = Blueprint('frontdesk', __name__)

@bp.route('/frontdesk/dashboard')
@login_required
def dashboard():
    if current_user.role != 'frontdesk':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    classes = Class.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('frontdesk_dashboard.html', classes=classes, teachers=teachers)

@bp.route('/frontdesk/add_class', methods=['POST'])
@login_required
def add_class():
    if current_user.role != 'frontdesk':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    name = request.form['name']
    date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    time = datetime.strptime(request.form['time'], '%H:%M').time()
    teacher_id = request.form['teacher_id']
    location = request.form['location']
    new_class = Class(name=name, date=date, time=time, teacher_id=teacher_id, location=location)
    db.session.add(new_class)
    db.session.commit()
    flash('Class added successfully')
    return redirect(url_for('frontdesk.dashboard'))

@bp.route('/frontdesk/add_attendee/<int:class_id>', methods=['POST'])
@login_required
def add_attendee(class_id):
    if current_user.role != 'frontdesk':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    name = request.form['name']
    stipend = 'stipend' in request.form
    group = request.form.get('group') or None
    comments = request.form.get('comments') or None
    group_hour = request.form.get('group_hour') or None
    group_type = request.form.get('group_type') or None
    time_in = datetime.strptime(request.form['time_in'], '%H:%M').time() if request.form.get('time_in') else None
    time_out = datetime.strptime(request.form['time_out'], '%H:%M').time() if request.form.get('time_out') else None
    new_attendee = Attendee(
        name=name,
        stipend=stipend,
        group=group,
        comments=comments,
        class_id=class_id,
        group_hour=group_hour,
        group_type=group_type,
        time_in=time_in,
        time_out=time_out
    )
    db.session.add(new_attendee)
    db.session.commit()
    flash('Attendee added successfully')
    return redirect(url_for('frontdesk.dashboard'))
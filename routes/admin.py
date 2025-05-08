from flask import Blueprint, render_template, redirect, url_for, request, flash, Response
from flask_login import login_required, current_user
from extensions import db
from models import Class, User, Attendee
from datetime import datetime, date
import csv
from io import StringIO

bp = Blueprint('admin', __name__)

@bp.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    classes = Class.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    users = User.query.all()
    return render_template('admin_dashboard.html', classes=classes, teachers=teachers, users=users)

@bp.route('/admin/add_class', methods=['POST'])
@login_required
def add_class():
    if current_user.role != 'admin':
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
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/edit_class/<int:class_id>', methods=['POST'])
@login_required
def edit_class(class_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    class_ = Class.query.get_or_404(class_id)
    class_.name = request.form['name']
    class_.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    class_.time = datetime.strptime(request.form['time'], '%H:%M').time()
    class_.teacher_id = request.form['teacher_id']
    class_.location = request.form['location']
    db.session.commit()
    flash('Class updated successfully')
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/delete_class/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    class_ = Class.query.get_or_404(class_id)
    db.session.delete(class_)
    db.session.commit()
    flash('Class deleted successfully')
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/add_attendee/<int:class_id>', methods=['POST'])
@login_required
def add_attendee(class_id):
    if current_user.role != 'admin':
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
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/edit_attendee/<int:attendee_id>', methods=['POST'])
@login_required
def edit_attendee(attendee_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    attendee = Attendee.query.get_or_404(attendee_id)
    attendee.name = request.form['name']
    attendee.stipend = 'stipend' in request.form
    attendee.group = request.form.get('group') or None
    attendee.comments = request.form.get('comments') or None
    attendee.checked_in = 'checked_in' in request.form
    attendee.group_hour = request.form.get('group_hour') or None
    attendee.group_type = request.form.get('group_type') or None
    attendee.time_in = datetime.strptime(request.form['time_in'], '%H:%M').time() if request.form.get('time_in') else None
    attendee.time_out = datetime.strptime(request.form['time_out'], '%H:%M').time() if request.form.get('time_out') else None
    db.session.commit()
    flash('Attendee updated successfully')
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/delete_attendee/<int:attendee_id>', methods=['POST'])
@login_required
def delete_attendee(attendee_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    attendee = Attendee.query.get_or_404(attendee_id)
    db.session.delete(attendee)
    db.session.commit()
    flash('Attendee deleted successfully')
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/add_user', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists')
        return redirect(url_for('admin.dashboard'))
    
    if role not in ['admin', 'frontdesk', 'teacher']:
        flash('Invalid role')
        return redirect(url_for('admin.dashboard'))
    
    new_user = User(username=username, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    flash('User added successfully')
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Cannot delete your own account')
        return redirect(url_for('admin.dashboard'))
    
    if user.role == 'teacher' and user.classes:
        flash('Cannot delete teacher with assigned classes')
        return redirect(url_for('admin.dashboard'))
        
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/report')
@login_required
def report():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    teacher_id = request.args.get('teacher_id')
    
    query = Class.query
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Class.date >= start_date)
        except ValueError:
            flash('Invalid start date')
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Class.date <= end_date)
        except ValueError:
            flash('Invalid end date')
    if teacher_id and teacher_id != 'all':
        query = query.filter_by(teacher_id=teacher_id)
    
    classes = query.order_by(Class.date, Class.time).all()
    teachers = User.query.filter_by(role='teacher').all()
    
    if request.args.get('format') == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Class Name', 'Date', 'Time', 'Teacher', 'Location', 'Attendee Name', 'Stipend', 'Group', 'Comments', 'Checked In', 'Group Hour', 'Group Type', 'Time In', 'Time Out'])
        for class_ in classes:
            for attendee in class_.attendees:
                writer.writerow([
                    class_.name,
                    class_.date,
                    class_.time,
                    class_.teacher.username,
                    class_.location,
                    attendee.name,
                    'Yes' if attendee.stipend else 'No',
                    attendee.group or '',
                    attendee.comments or '',
                    'Yes' if attendee.checked_in else 'No',
                    attendee.group_hour or '',
                    attendee.group_type or '',
                    attendee.time_in.strftime('%H:%M') if attendee.time_in else '',
                    attendee.time_out.strftime('%H:%M') if attendee.time_out else ''
                ])
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=wellness_report.csv'}
        )
    
    return render_template('report.html', classes=classes, teachers=teachers)
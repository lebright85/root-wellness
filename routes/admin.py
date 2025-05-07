from flask import Blueprint, render_template, redirect, url_for, request, flash, Response
from flask_login import login_required, current_user
from extensions import db
from models import Class, User, Attendee
from datetime import datetime
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
    return render_template('admin_dashboard.html', classes=classes, teachers=teachers)

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
    new_attendee = Attendee(name=name, stipend=stipend, group=group, comments=comments, class_id=class_id)
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
    db.session.commit()
    flash('Attendee updated successfully')
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/report')
@login_required
def report():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('auth.login'))
    
    classes = Class.query.order_by(Class.date, Class.time).all()
    
    if request.args.get('format') == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Class Name', 'Date', 'Time', 'Teacher', 'Location', 'Attendee Name', 'Stipend', 'Group', 'Comments', 'Checked In'])
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
                    'Yes' if attendee.checked_in else 'No'
                ])
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=wellness_report.csv'}
        )
    
    return render_template('report.html', classes=classes)
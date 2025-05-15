from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models import Class, Attendee, User
from extensions import db
from datetime import datetime, time, date
from werkzeug.security import generate_password_hash
import csv
import io

bp = Blueprint('admin', __name__)

@bp.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('admin_dashboard.html')

@bp.route('/admin/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if current_user.role != 'admin':
        flash('Access denied: Admins only.', 'danger')
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
        
        # Edit Class
        elif 'edit_class' in request.form:
            try:
                class_id = int(request.form['class_id'])
                class_ = Class.query.get_or_404(class_id)
                class_.name = request.form['edit_class_name']
                class_.date = datetime.strptime(request.form['edit_class_date'], '%Y-%m-%d').date()
                class_.time = datetime.strptime(request.form['edit_class_time'], '%H:%M').time()
                class_.teacher_id = int(request.form['edit_teacher_id'])
                class_.location = request.form['edit_location']
                db.session.commit()
                flash('Class updated successfully.', 'success')
            except ValueError as e:
                flash(f'Error updating class: {str(e)}', 'danger')
        
        # Add Attendee
        elif 'add_attendee' in request.form:
            try:
                attendee_id = request.form.get('attendee_id') or None
                attendee_name = request.form['attendee_name']
                class_id = int(request.form['class_id'])
                engagement = 'engagement' in request.form
                group = request.form['group'] or None
                group_hour = request.form['group_hour'] or None
                group_type = request.form['group_type'] or None
                time_in = datetime.strptime(request.form['time_in'], '%H:%M').time() if request.form['time_in'] else None
                time_out = datetime.strptime(request.form['time_out'], '%H:%M').time() if request.form['time_out'] else None
                comments = request.form['comments'] or None
                
                if attendee_id and Attendee.query.filter_by(attendee_id=attendee_id).first():
                    flash('Attendee ID already exists.', 'danger')
                    return redirect(url_for('admin.manage'))
                
                new_attendee = Attendee(
                    attendee_id=attendee_id,
                    name=attendee_name,
                    class_id=class_id,
                    stipend=engagement,
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
        
        # Edit Attendee
        elif 'edit_attendee' in request.form:
            try:
                attendee_id = int(request.form['attendee_id'])
                attendee = Attendee.query.get_or_404(attendee_id)
                attendee.name = request.form['edit_attendee_name']
                attendee.class_id = int(request.form['edit_class_id'])
                attendee.stipend = 'edit_engagement' in request.form
                attendee.group = request.form['edit_group'] or None
                attendee.group_hour = request.form['edit_group_hour'] or None
                attendee.group_type = request.form['edit_group_type'] or None
                attendee.time_in = datetime.strptime(request.form['edit_time_in'], '%H:%M').time() if request.form['edit_time_in'] else None
                attendee.time_out = datetime.strptime(request.form['edit_time_out'], '%H:%M').time() if request.form['edit_time_out'] else None
                attendee.comments = request.form['edit_comments'] or None
                db.session.commit()
                flash('Attendee updated successfully.', 'success')
            except ValueError as e:
                flash(f'Error updating attendee: {str(e)}', 'danger')
        
        # Delete Class
        elif 'delete_class' in request.form:
            class_id = int(request.form['class_id'])
            class_ = Class.query.get_or_404(class_id)
            db.session.delete(class_)
            db.session.commit()
            flash('Class deleted successfully.', 'success')
        
        # Delete Attendee
        elif 'delete_attendee' in request.form:
            attendee_id = int(request.form['attendee_id'])
            attendee = Attendee.query.get_or_404(attendee_id)
            db.session.delete(attendee)
            db.session.commit()
            flash('Attendee deleted successfully.', 'success')
        
        return redirect(url_for('admin.manage'))
    
    return render_template('admin_manage.html', classes=classes, teachers=teachers)

@bp.route('/admin/report', methods=['GET', 'POST'])
@login_required
def report():
    if current_user.role != 'admin':
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('auth.login'))
    
    start_date = None
    end_date = None
    classes_query = Class.query
    
    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                classes_query = classes_query.filter(Class.date >= start_date)
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                classes_query = classes_query.filter(Class.date <= end_date)
            
            if start_date and end_date and start_date > end_date:
                flash('Start date must be before or equal to end date.', 'danger')
                return redirect(url_for('admin.report'))
                
        except ValueError as e:
            flash(f'Invalid date format: {str(e)}', 'danger')
            return redirect(url_for('admin.report'))
    
    classes = classes_query.all()
    total_classes = len(classes)
    total_attendees = sum(len(class_.attendees) for class_ in classes)
    checked_in_attendees = sum(len([a for a in class_.attendees if a.checked_in]) for class_ in classes)
    
    # Store date range in session for download_report
    from flask import session
    session['report_start_date'] = start_date.strftime('%Y-%m-%d') if start_date else None
    session['report_end_date'] = end_date.strftime('%Y-%m-%d') if end_date else None
    
    return render_template('report.html', 
                         classes=classes, 
                         total_classes=total_classes, 
                         total_attendees=total_attendees, 
                         checked_in_attendees=checked_in_attendees,
                         start_date=start_date,
                         end_date=end_date)

@bp.route('/admin/download_report')
@login_required
def download_report():
    if current_user.role != 'admin':
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('admin.report'))
    
    from flask import session
    start_date = None
    end_date = None
    classes_query = Class.query
    
    try:
        start_date_str = session.get('report_start_date')
        end_date_str = session.get('report_end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            classes_query = classes_query.filter(Class.date >= start_date)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            classes_query = classes_query.filter(Class.date <= end_date)
            
        if start_date and end_date and start_date > end_date:
            flash('Invalid date range in session.', 'danger')
            return redirect(url_for('admin.report'))
            
    except ValueError as e:
        flash(f'Invalid date format in session: {str(e)}', 'danger')
        return redirect(url_for('admin.report'))
    
    classes = classes_query.all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    headers = [
        'Class Name', 'Date', 'Time', 'Location', 'Counselor', 'Credential',
        'Attendee Name', 'Attendee ID', 'Engagement', 'Group', 'Group Hour', 'Group Type',
        'Time In', 'Time Out', 'Comments', 'Checked In'
    ]
    writer.writerow(headers)
    
    # Write data
    for class_ in classes:
        for attendee in class_.attendees:
            row = [
                class_.name,
                class_.date.strftime('%Y-%m-%d'),
                class_.time.strftime('%H:%M'),
                class_.location,
                class_.teacher.username,
                class_.teacher.department or '',
                attendee.name,
                attendee.attendee_id or '',
                'Yes' if attendee.stipend else 'No',
                attendee.group or '',
                attendee.group_hour or '',
                attendee.group_type or '',
                attendee.time_in.strftime('%H:%M') if attendee.time_in else '',
                attendee.time_out.strftime('%H:%M') if attendee.time_out else '',
                attendee.comments or '',
                'Yes' if attendee.checked_in else 'No'
            ]
            writer.writerow(row)
        # Add class row with no attendee data if no attendees
        if not class_.attendees:
            row = [
                class_.name,
                class_.date.strftime('%Y-%m-%d'),
                class_.time.strftime('%H:%M'),
                class_.location,
                class_.teacher.username,
                class_.teacher.department or '',
                '', '', '', '', '', '', '', '', '', ''
            ]
            writer.writerow(row)
    
    # Prepare file for download
    output.seek(0)
    filename = f"report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv" if start_date and end_date else 'report.csv'
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.role != 'admin':
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('auth.login'))
    
    users = User.query.all()
    
    if request.method == 'POST':
        # Add User
        if 'add_user' in request.form:
            try:
                username = request.form['username']
                password = request.form['password']
                role = request.form['role']
                department = request.form.get('department') or None
                
                if User.query.filter_by(username=username).first():
                    flash('Username already exists.', 'danger')
                    return redirect(url_for('admin.users'))
                
                if role not in ['admin', 'frontdesk', 'teacher']:
                    flash('Invalid role.', 'danger')
                    return redirect(url_for('admin.users'))
                
                new_user = User(username=username, role=role, department=department)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash('User added successfully.', 'success')
            except Exception as e:
                flash(f'Error adding user: {str(e)}', 'danger')
        
        # Edit User
        elif 'edit_user' in request.form:
            try:
                user_id = int(request.form['user_id'])
                user = User.query.get_or_404(user_id)
                username = request.form['edit_username']
                password = request.form['edit_password']
                role = request.form['edit_role']
                department = request.form.get('edit_department') or None
                
                if username != user.username and User.query.filter_by(username=username).first():
                    flash('Username already exists.', 'danger')
                    return redirect(url_for('admin.users'))
                
                if role not in ['admin', 'frontdesk', 'teacher']:
                    flash('Invalid role.', 'danger')
                    return redirect(url_for('admin.users'))
                
                user.username = username
                if password:
                    user.set_password(password)
                user.role = role
                user.department = department
                db.session.commit()
                flash('User updated successfully.', 'success')
            except ValueError as e:
                flash(f'Error updating user: {str(e)}', 'danger')
        
        # Delete User
        elif 'delete_user' in request.form:
            try:
                user_id = int(request.form['user_id'])
                user = User.query.get_or_404(user_id)
                
                if user.id == current_user.id:
                    flash('Cannot delete your own account.', 'danger')
                    return redirect(url_for('admin.users'))
                
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully.', 'success')
            except ValueError as e:
                flash(f'Error deleting user: {str(e)}', 'danger')
        
        return redirect(url_for('admin.users'))
    
    return render_template('admin_users.html', users=users)
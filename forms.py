from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TimeField
from wtforms.validators import DataRequired

class AddAttendeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    stipend = SelectField('Stipend', choices=[('yes', 'Yes'), ('no', 'No')])
    attendance_status = SelectField('Attendance Status', choices=[('present', 'Present'), ('absent', 'Absent'), ('excused', 'Excused')])
    group_hour = StringField('Group Hour', validators=[DataRequired()])
    group_type = SelectField('Group Type', choices=[('yoga', 'Yoga'), ('meditation', 'Meditation')])
    time_out = TimeField('Time Out', format='%H:%M')
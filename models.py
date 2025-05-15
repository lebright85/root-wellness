from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, frontdesk, teacher
    department = db.Column(db.String(100), nullable=True)
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    teacher = db.relationship('User', backref=db.backref('classes', lazy=True))
    attendees = db.relationship('Attendee', backref='class_', lazy=True)

class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attendee_id = db.Column(db.String(50), unique=True, nullable=True)  # New attendee_id field
    name = db.Column(db.String(100), nullable=False)
    stipend = db.Column(db.Boolean, default=False)
    group = db.Column(db.String(100))
    group_hour = db.Column(db.String(50))
    group_type = db.Column(db.String(50))
    time_in = db.Column(db.Time)
    time_out = db.Column(db.Time)
    comments = db.Column(db.Text)
    checked_in = db.Column(db.Boolean, default=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
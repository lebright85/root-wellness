from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import time
from extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, frontdesk, teacher

    classes = db.relationship('Class', backref='teacher', lazy=True)

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

    attendees = db.relationship('Attendee', backref='class_ref', lazy=True, cascade="all, delete-orphan")

class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stipend = db.Column(db.Boolean, default=False)
    group = db.Column(db.String(50), nullable=True)
    comments = db.Column(db.String(200), nullable=True)
    checked_in = db.Column(db.Boolean, default=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    group_hour = db.Column(db.String(50), nullable=True)  # e.g., "1 hr" or "10:00 AM"
    group_type = db.Column(db.String(50), nullable=True)  # e.g., "Beginners", "Advanced"
    time_in = db.Column(db.Time, nullable=True)  # Check-in time
    time_out = db.Column(db.Time, nullable=True)  # Check-out time
from app import app, db
from models import User, Class, Attendee
from datetime import date, time

with app.app_context():
    # Create tables (if not already created by migration)
    db.create_all()
    
    # Create admin user
    if not User.query.filter_by(username='admin1').first():
        admin = User(username='admin1', role='admin')
        admin.set_password('test123')
        db.session.add(admin)
        print("Created admin user: admin1, password: test123")
    
    # Create teacher user
    if not User.query.filter_by(username='teacher1').first():
        teacher = User(username='teacher1', role='teacher')
        teacher.set_password('test123')
        db.session.add(teacher)
        print("Created teacher user: teacher1, password: test123")
    
    # Create test class
    if not Class.query.filter_by(name='Yoga Basics').first():
        teacher = User.query.filter_by(username='teacher1').first()
        if teacher:
            class_ = Class(
                name='Yoga Basics',
                date=date(2025, 5, 10),
                time=time(9, 0),
                teacher_id=teacher.id,
                location='Studio A'
            )
            db.session.add(class_)
            print("Created class: Yoga Basics")
    
    # Create test attendee
    if not Attendee.query.filter_by(name='John Doe').first():
        class_ = Class.query.filter_by(name='Yoga Basics').first()
        if class_:
            attendee = Attendee(
                name='John Doe',
                stipend=True,
                group='Morning',
                group_hour='1 hr',
                group_type='Beginners',
                time_in=time(9, 0),
                time_out=time(10, 0),
                comments='First class',
                checked_in=False,
                class_id=class_.id
            )
            db.session.add(attendee)
            print("Created attendee: John Doe")
    
    db.session.commit()
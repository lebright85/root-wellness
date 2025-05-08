from app import app, db
from models import User, Class, Attendee
from datetime import date, time

with app.app_context():
    # Create tables
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
    
    # Create front desk user
    if not User.query.filter_by(username='frontdesk1').first():
        frontdesk = User(username='frontdesk1', role='frontdesk')
        frontdesk.set_password('test123')
        db.session.add(frontdesk)
        print("Created front desk user: frontdesk1, password: test123")
    
    # Create test classes
    if not Class.query.filter_by(name='Yoga Basics').first():
        teacher = User.query.filter_by(username='teacher1').first()
        if teacher:
            class1 = Class(
                name='Yoga Basics',
                date=date(2025, 5, 10),
                time=time(9, 0),
                teacher_id=teacher.id,
                location='Studio A'
            )
            class2 = Class(
                name='Advanced Yoga',
                date=date(2025, 5, 11),
                time=time(11, 0),
                teacher_id=teacher.id,
                location='Studio B'
            )
            db.session.add_all([class1, class2])
            print("Created classes: Yoga Basics, Advanced Yoga")
    
    # Create test attendees
    if not Attendee.query.filter_by(name='John Doe').first():
        class1 = Class.query.filter_by(name='Yoga Basics').first()
        class2 = Class.query.filter_by(name='Advanced Yoga').first()
        if class1 and class2:
            attendee1 = Attendee(
                name='John Doe',
                stipend=True,
                group='Morning',
                group_hour='1 hr',
                group_type='Beginners',
                time_in=time(9, 0),
                time_out=time(10, 0),
                comments='First class',
                checked_in=False,
                class_id=class1.id
            )
            attendee2 = Attendee(
                name='Jane Smith',
                stipend=False,
                group='Midday',
                group_hour='1.5 hr',
                group_type='Advanced',
                time_in=time(11, 0),
                time_out=time(12, 30),
                comments='Returning student',
                checked_in=False,
                class_id=class2.id
            )
            db.session.add_all([attendee1, attendee2])
            print("Created attendees: John Doe, Jane Smith")
    
    db.session.commit()
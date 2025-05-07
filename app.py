from flask import Flask, redirect, url_for
import os
from extensions import db, login_manager
from models import User

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

# Use PostgreSQL database URL from environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'root_wellness.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Default route to redirect to login
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# Import and register blueprints after app initialization
from routes import auth, admin, teacher, frontdesk
app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(teacher.bp)
app.register_blueprint(frontdesk.bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run()
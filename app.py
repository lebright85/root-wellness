from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from extensions import db
import logging
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)
app.config.from_object(Config)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Log template search path and available templates
env = Environment(loader=FileSystemLoader('templates'))
app.logger.debug(f"Template search path: {app.jinja_loader.searchpath}")
app.logger.debug(f"Available templates: {env.list_templates()}")

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
migrate = Migrate(app, db)

# Register blueprints
from routes import auth, admin, frontdesk, teacher
app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(frontdesk.bp)
app.register_blueprint(teacher.bp)

# Root route to redirect to login
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)
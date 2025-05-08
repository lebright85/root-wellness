import os

class Config:
    # Secret key for session management (generate a secure one for production)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'attendance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Other Flask settings
    SESSION_COOKIE_SECURE = True  # Use secure cookies in production
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
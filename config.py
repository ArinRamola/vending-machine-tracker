import os
import secrets

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    DATABASE_NAME = 'database.db'
    
    # Session configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Flask configuration
    DEBUG = False
    TESTING = False
    
    # Upload folders
    UPLOAD_FOLDER = 'static/uploads'
    QR_FOLDER = 'static/qrcodes'
    CHART_FOLDER = 'static/charts'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_NAME = 'database.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    # In production, always use environment variable for SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production!")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_NAME = 'test_database.db'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
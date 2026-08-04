import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_FILE = BASE_DIR / 'restaurant.db'

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'change-this-secret-key'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or f'sqlite:///{DATABASE_FILE.as_posix()}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'static' / 'images'))
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

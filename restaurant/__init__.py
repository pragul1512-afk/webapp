import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / 'templates'),
        static_folder=str(BASE_DIR / 'static'),
    )

    @app.template_filter('format_currency')
    def format_currency(value):
        try:
            amount = float(value)
        except (TypeError, ValueError):
            return '₹0.00'
        return f'₹{amount:,.2f}'
    if os.path.exists(str(BASE_DIR / '.env')):
        from dotenv import load_dotenv

        load_dotenv(str(BASE_DIR / '.env'))
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to continue.'

    with app.app_context():
        from . import models

        db.create_all()

    from .routes import main_bp, auth_bp, admin_bp, api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app


from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

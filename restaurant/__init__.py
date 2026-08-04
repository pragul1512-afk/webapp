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


def seed_default_data():
    from .models import Admin, FoodCategory, FoodItem, Table, User

    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)

    if not User.query.filter_by(email='demo@example.com').first():
        user = User(name='Demo Customer', email='demo@example.com', phone='+15551234567', address='123 Flavor Street')
        user.set_password('password123')
        db.session.add(user)

    FoodItem.query.update({FoodItem.image_filename: None})

    if FoodCategory.query.count() == 0:
        categories = [
            FoodCategory(name='Starters', description='Small plates to begin your meal.'),
            FoodCategory(name='Main Course', description='Hearty entrees for every appetite.'),
            FoodCategory(name='Desserts', description='Sweet treats to finish your order.'),
            FoodCategory(name='Beverages', description='Cool drinks and hot cups.'),
        ]
        db.session.add_all(categories)
        db.session.flush()
        items = [
            FoodItem(category_id=categories[0].id, name='Bruschetta', description='Toasted bread with tomatoes and basil.', price=250.00),
            FoodItem(category_id=categories[0].id, name='Garlic Fries', description='Crispy fries with garlic and herbs.', price=180.00),
            FoodItem(category_id=categories[1].id, name='Grilled Salmon', description='Salmon fillet served with seasonal vegetables.', price=1800.00),
            FoodItem(category_id=categories[1].id, name='Spicy Chicken Curry', description='Aromatic curry with tender chicken pieces.', price=320.00),
            FoodItem(category_id=categories[2].id, name='Chocolate Lava Cake', description='Warm chocolate cake with molten center.', price=350.00),
            FoodItem(category_id=categories[3].id, name='Classic Lemonade', description='Fresh lemonade for a refreshing sip.', price=120.00),
        ]
        db.session.add_all(items)

    if Table.query.count() == 0:
        tables = [
            Table(table_number='A1', capacity=2, location='Window'),
            Table(table_number='A2', capacity=4, location='Window'),
            Table(table_number='B1', capacity=4, location='Center'),
            Table(table_number='B2', capacity=6, location='Center'),
            Table(table_number='C1', capacity=8, location='Private'),
        ]
        db.session.add_all(tables)

    db.session.commit()


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
        seed_default_data()

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

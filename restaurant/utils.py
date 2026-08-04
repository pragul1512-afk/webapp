from functools import wraps
from flask import session, redirect, url_for, flash


def admin_login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('admin_id'):
            flash('Please log in as admin to access that page.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return wrapped


def calculate_cart_totals(cart_items):
    subtotal = sum(item.quantity * float(item.item.price) for item in cart_items)
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + tax, 2)
    return subtotal, tax, total


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webp', 'gif'}

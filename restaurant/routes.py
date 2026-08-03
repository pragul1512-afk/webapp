from datetime import datetime, timedelta
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    abort,
    jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from .models import (
    User,
    Admin,
    FoodCategory,
    FoodItem,
    Table,
    TableBooking,
    CartItem,
    Order,
    OrderItem,
    Payment,
)
from .forms import (
    RegisterForm,
    LoginForm,
    ProfileForm,
    BookingForm,
    CategoryForm,
    FoodItemForm,
    TableForm,
    AdminLoginForm,
    OrderStatusForm,
    PaymentForm,
)
from .utils import admin_login_required, calculate_cart_totals

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)
api_bp = Blueprint('api', __name__)


@main_bp.route('/')
def index():
    categories = FoodCategory.query.order_by(FoodCategory.name).all()
    featured = FoodItem.query.filter_by(is_available=True).order_by(FoodItem.created_at.desc()).limit(8).all()
    return render_template('index.html', categories=categories, featured=featured)


@main_bp.route('/menu')
def menu():
    categories = FoodCategory.query.order_by(FoodCategory.name).all()
    search = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    query = FoodItem.query.filter_by(is_available=True)
    if search:
        query = query.filter(FoodItem.name.ilike(f'%{search}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    menu_items = query.order_by(FoodItem.name).all()
    return render_template('menu.html', categories=categories, menu_items=menu_items, search=search, selected_category=category_id)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash('Email address already registered.', 'danger')
            return render_template('register.html', form=form)

        user = User(
            name=form.name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            address=form.address.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Signed in successfully.', 'success')
            return redirect(url_for('main.index'))

        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are now logged out.', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('main.profile'))
    return render_template('profile.html', form=form)


def find_available_table(guest_count, booking_date, booking_time):
    candidate_tables = Table.query.filter(Table.capacity >= guest_count, Table.is_available.is_(True)).order_by(Table.capacity).all()
    for table in candidate_tables:
        conflict = TableBooking.query.filter(
            TableBooking.table_id == table.id,
            TableBooking.booking_date == booking_date,
            TableBooking.booking_time == booking_time,
            TableBooking.status.in_(['Pending', 'Approved'])
        ).first()
        if not conflict:
            return table
    return None


@main_bp.route('/book-table', methods=['GET', 'POST'])
@login_required
def book_table():
    form = BookingForm()
    if form.validate_on_submit():
        table = find_available_table(form.guests.data, form.booking_date.data, form.booking_time.data)
        if not table:
            flash('No tables are available for the selected date and time.', 'warning')
            return render_template('booking.html', form=form)

        booking = TableBooking(
            user=current_user,
            table=table,
            guests=form.guests.data,
            booking_date=form.booking_date.data,
            booking_time=form.booking_time.data,
            special_request=form.special_request.data,
            status='Pending',
        )
        db.session.add(booking)
        db.session.commit()
        flash('Table reservation submitted. The restaurant staff will confirm shortly.', 'success')
        return redirect(url_for('main.bookings'))

    return render_template('booking.html', form=form)


@main_bp.route('/bookings')
@login_required
def bookings():
    bookings = TableBooking.query.filter_by(user_id=current_user.id).order_by(TableBooking.booking_date.desc(), TableBooking.booking_time.desc()).all()
    return render_template('bookings.html', bookings=bookings)


@main_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = TableBooking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()
    if booking.status in ['Cancelled', 'Rejected']:
        flash('Booking is already closed.', 'info')
        return redirect(url_for('main.bookings'))

    booking.status = 'Cancelled'
    db.session.commit()
    flash('Booking cancelled successfully.', 'success')
    return redirect(url_for('main.bookings'))


@main_bp.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal, tax, total = calculate_cart_totals(items)
    return render_template('cart.html', cart_items=items, subtotal=subtotal, tax=tax, total=total)


@main_bp.route('/cart/add/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item = FoodItem.query.get_or_404(item_id)
    cart_item = CartItem.query.filter_by(user_id=current_user.id, item_id=item.id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user=current_user, item=item, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    flash(f'Added {item.name} to cart.', 'success')
    return redirect(request.referrer or url_for('main.menu'))


@main_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, item_id=item_id).first_or_404()
    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        quantity = 1
    if quantity < 1:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    db.session.commit()
    flash('Cart updated.', 'success')
    return redirect(url_for('main.cart'))


@main_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_cart_item(item_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, item_id=item_id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('main.cart'))


@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('main.menu'))

    subtotal, tax, total = calculate_cart_totals(items)
    form = PaymentForm()
    if form.validate_on_submit():
        order = Order(
            user=current_user,
            total_amount=total,
            tax_amount=tax,
            status='Pending',
            payment_method=form.method.data,
            payment_status='Pending' if form.method.data == 'Cash on Delivery' else 'Paid',
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            order_item = OrderItem(
                order=order,
                item_id=item.item.id,
                quantity=item.quantity,
                unit_price=item.item.price,
            )
            db.session.add(order_item)
        payment = Payment(
            order=order,
            amount=total,
            method=form.method.data,
            status='Success' if form.method.data == 'Online Payment' else 'Pending',
            transaction_id=f'TXN-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
            paid_at=datetime.utcnow() if form.method.data == 'Online Payment' else None,
        )
        db.session.add(payment)
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash('Your order has been placed successfully.', 'success')
        return redirect(url_for('main.order_detail', order_id=order.id))

    return render_template('checkout.html', cart_items=items, subtotal=subtotal, tax=tax, total=total, form=form)


@main_bp.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)


@main_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('order_detail.html', order=order)


@main_bp.route('/contact')
def contact():
    return render_template('contact.html')


@api_bp.route('/menu')
def api_menu():
    categories = FoodCategory.query.order_by(FoodCategory.name).all()
    payload = []
    for category in categories:
        payload.append({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'items': [
                {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'price': float(item.price),
                    'image': item.image_filename,
                    'available': item.is_available,
                }
                for item in category.menu_items if item.is_available
            ],
        })
    return jsonify({'categories': payload})


@api_bp.route('/bookings')
@login_required
def api_user_bookings():
    bookings = TableBooking.query.filter_by(user_id=current_user.id).order_by(TableBooking.booking_date.desc()).all()
    return jsonify([
        {
            'id': booking.id,
            'table': booking.table.table_number,
            'guests': booking.guests,
            'date': booking.booking_date.isoformat(),
            'time': booking.booking_time.strftime('%H:%M'),
            'status': booking.status,
        }
        for booking in bookings
    ])


@api_bp.route('/orders/<int:order_id>')
@login_required
def api_order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': order.id,
        'total': float(order.total_amount),
        'tax': float(order.tax_amount),
        'status': order.status,
        'payment_method': order.payment_method,
        'payment_status': order.payment_status,
        'items': [
            {
                'name': item.item.name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
            }
            for item in order.items
        ],
    })


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            session['admin_id'] = admin.id
            session.permanent = True
            flash('Admin access granted.', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    flash('Admin signed out.', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@admin_login_required
def dashboard():
    total_customers = User.query.count()
    total_orders = Order.query.count()
    pending_bookings = TableBooking.query.filter_by(status='Pending').count()
    sales = db.session.query(db.func.coalesce(db.func.sum(Payment.amount), 0)).filter(Payment.status == 'Success').scalar() or 0
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', total_customers=total_customers, total_orders=total_orders, pending_bookings=pending_bookings, sales=float(sales), recent_orders=recent_orders)


@admin_bp.route('/categories')
@admin_login_required
def categories():
    categories = FoodCategory.query.order_by(FoodCategory.name).all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@admin_login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = FoodCategory(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/category_form.html', form=form, title='Add Category')


@admin_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def edit_category(category_id):
    category = FoodCategory.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/category_form.html', form=form, title='Edit Category')


@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_login_required
def delete_category(category_id):
    category = FoodCategory.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category removed.', 'info')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/items')
@admin_login_required
def items():
    items = FoodItem.query.order_by(FoodItem.name).all()
    return render_template('admin/items.html', items=items)


def prepare_item_form(form):
    form.category_id.choices = [(c.id, c.name) for c in FoodCategory.query.order_by(FoodCategory.name).all()]


@admin_bp.route('/items/add', methods=['GET', 'POST'])
@admin_login_required
def add_item():
    form = FoodItemForm()
    prepare_item_form(form)
    if form.validate_on_submit():
        item = FoodItem(
            category_id=form.category_id.data,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image_filename=form.image_filename.data or 'images/placeholder.png',
            is_available=form.is_available.data,
        )
        db.session.add(item)
        db.session.commit()
        flash('Menu item added.', 'success')
        return redirect(url_for('admin.items'))
    return render_template('admin/item_form.html', form=form, title='Add Food Item')


@admin_bp.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def edit_item(item_id):
    item = FoodItem.query.get_or_404(item_id)
    form = FoodItemForm(obj=item)
    prepare_item_form(form)
    if form.validate_on_submit():
        item.category_id = form.category_id.data
        item.name = form.name.data
        item.description = form.description.data
        item.price = form.price.data
        item.image_filename = form.image_filename.data or item.image_filename
        item.is_available = form.is_available.data
        db.session.commit()
        flash('Menu item updated.', 'success')
        return redirect(url_for('admin.items'))
    return render_template('admin/item_form.html', form=form, title='Edit Food Item')


@admin_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@admin_login_required
def delete_item(item_id):
    item = FoodItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted.', 'info')
    return redirect(url_for('admin.items'))


@admin_bp.route('/tables')
@admin_login_required
def tables():
    tables = Table.query.order_by(Table.table_number).all()
    return render_template('admin/tables.html', tables=tables)


@admin_bp.route('/tables/add', methods=['GET', 'POST'])
@admin_login_required
def add_table():
    form = TableForm()
    if form.validate_on_submit():
        table = Table(
            table_number=form.table_number.data,
            capacity=form.capacity.data,
            location=form.location.data,
            is_available=form.is_available.data,
        )
        db.session.add(table)
        db.session.commit()
        flash('Table added successfully.', 'success')
        return redirect(url_for('admin.tables'))
    return render_template('admin/table_form.html', form=form, title='Add Table')


@admin_bp.route('/tables/<int:table_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def edit_table(table_id):
    table = Table.query.get_or_404(table_id)
    form = TableForm(obj=table)
    if form.validate_on_submit():
        table.table_number = form.table_number.data
        table.capacity = form.capacity.data
        table.location = form.location.data
        table.is_available = form.is_available.data
        db.session.commit()
        flash('Table updated successfully.', 'success')
        return redirect(url_for('admin.tables'))
    return render_template('admin/table_form.html', form=form, title='Edit Table')


@admin_bp.route('/tables/<int:table_id>/delete', methods=['POST'])
@admin_login_required
def delete_table(table_id):
    table = Table.query.get_or_404(table_id)
    db.session.delete(table)
    db.session.commit()
    flash('Table removed.', 'info')
    return redirect(url_for('admin.tables'))


@admin_bp.route('/bookings')
@admin_login_required
def bookings_admin():
    bookings = TableBooking.query.order_by(TableBooking.booking_date.desc(), TableBooking.booking_time.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)


@admin_bp.route('/bookings/<int:booking_id>/action', methods=['POST'])
@admin_login_required
def booking_action(booking_id):
    booking = TableBooking.query.get_or_404(booking_id)
    action = request.form.get('action')
    if action == 'approve':
        booking.status = 'Approved'
        flash('Booking approved.', 'success')
    elif action == 'reject':
        booking.status = 'Rejected'
        flash('Booking rejected.', 'warning')
    else:
        flash('No action taken.', 'info')
    db.session.commit()
    return redirect(url_for('admin.bookings_admin'))


@admin_bp.route('/orders')
@admin_login_required
def orders_admin():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/orders/<int:order_id>/status', methods=['GET', 'POST'])
@admin_login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderStatusForm(status=order.status)
    if form.validate_on_submit():
        order.status = form.status.data
        if order.status == 'Delivered':
            order.payment.status = 'Success'
        db.session.commit()
        flash('Order status updated.', 'success')
        return redirect(url_for('admin.orders_admin'))
    return render_template('admin/order_status.html', form=form, order=order)


@admin_bp.route('/customers')
@admin_login_required
def customers():
    customers = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/customers.html', customers=customers)


@admin_bp.route('/reports')
@admin_login_required
def reports():
    recent_sales = (
        db.session.query(Payment)
        .filter(Payment.status == 'Success')
        .order_by(Payment.paid_at.desc())
        .limit(10)
        .all()
    )
    monthly_sales = (
        db.session.query(db.func.coalesce(db.func.sum(Payment.amount), 0))
        .filter(Payment.status == 'Success', Payment.paid_at >= datetime.utcnow() - timedelta(days=30))
        .scalar()
    )
    daily_report = (
        db.session.query(
            db.func.date(Payment.paid_at).label('date'),
            db.func.coalesce(db.func.sum(Payment.amount), 0).label('total')
        )
        .filter(Payment.status == 'Success', Payment.paid_at != None)
        .group_by(db.func.date(Payment.paid_at))
        .order_by(db.func.date(Payment.paid_at).desc())
        .limit(7)
        .all()
    )
    return render_template('admin/reports.html', monthly_sales=float(monthly_sales or 0), recent_sales=recent_sales, daily_report=daily_report)

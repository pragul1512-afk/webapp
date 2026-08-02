from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DecimalField, TextAreaField, BooleanField, DateField, TimeField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[Optional(), Length(max=30)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=30)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Update Profile')


class BookingForm(FlaskForm):
    guests = IntegerField('Guests', validators=[DataRequired(), NumberRange(min=1, max=20)])
    booking_date = DateField('Date', validators=[DataRequired()])
    booking_time = TimeField('Time', validators=[DataRequired()])
    special_request = TextAreaField('Special Request', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Reserve Table')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=80)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Save Category')


class FoodItemForm(FlaskForm):
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=255)])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    image_filename = StringField('Image Filename', validators=[Optional(), Length(max=255)])
    is_available = BooleanField('Available', default=True)
    submit = SubmitField('Save Food Item')


class TableForm(FlaskForm):
    table_number = StringField('Table Number', validators=[DataRequired(), Length(max=20)])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1, max=20)])
    location = StringField('Location', validators=[Optional(), Length(max=120)])
    is_available = BooleanField('Available', default=True)
    submit = SubmitField('Save Table')


class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Admin Login')


class OrderStatusForm(FlaskForm):
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Preparing', 'Preparing'), ('Ready', 'Ready'), ('Delivered', 'Delivered')], validators=[DataRequired()])
    submit = SubmitField('Update Status')


class PaymentForm(FlaskForm):
    method = RadioField('Payment Method', choices=[('Cash on Delivery', 'Cash on Delivery'), ('Online Payment', 'Online Payment')], default='Cash on Delivery', validators=[DataRequired()])
    submit = SubmitField('Place Order')

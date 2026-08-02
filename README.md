# Restaurant Table Booking and Food Ordering System

This project is a Python-based full-stack restaurant reservation and food ordering system powered by Flask and SQLAlchemy.

## Features
- User registration, login, and profile management
- Table booking with time slot availability checks
- Food menu browsing with search and category filters
- Persistent cart and checkout with cash or online payment simulation
- Order history and tracking
- Admin portal for managing categories, menu items, tables, bookings, and orders
- REST API endpoints for menu, bookings, and order details
- Session authentication and server-side validation

## Folder Structure
- `app.py` - Application entrypoint
- `restaurant/` - Flask application package
- `templates/` - Jinja2 page templates
- `static/` - CSS, JavaScript, and static assets
- `schema.sql` - Database schema definitions
- `sample_data.sql` - Sample insert statements
- `seed.py` - Script to populate sample data

## Requirements
- Python 3.10+
- MySQL server (optional; SQLite is used by default)

## Installation
1. Change to the project directory:
   ```powershell
   cd C:\Users\Dell\Videos\OneDrive\Desktop\app\app\webapp
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. (Optional) Create a `.env` file and set MySQL connection details:
   ```text
   SECRET_KEY=your-secret-key
   DATABASE_URL=mysql+pymysql://user:password@host/restaurant_db
   UPLOAD_FOLDER=static/images
   ```
4. Run the seed script to create tables and sample records:
   ```powershell
   python seed.py
   ```
5. Start the Flask application:
   ```powershell
   python app.py
   ```

Open `http://localhost:5000` in your browser.

## Admin Access
- Username: `admin`
- Password: `admin123`

## Database Schema
See `schema.sql` for a complete relational schema. Use MySQL to execute the script if you prefer the MySQL database backend.

## API Endpoints
- `GET /api/menu` - Returns menu categories and available items
- `GET /api/bookings` - Returns current user's bookings
- `GET /api/orders/<order_id>` - Returns details for a user order

## Notes
- The application supports both SQLite and MySQL by changing the `DATABASE_URL` environment variable.
- Cart data is stored in the database for persistent user sessions.
- Admin access is separate from the customer experience.

## GitHub Actions
A workflow is included at `.github/workflows/python-app.yml` to:
- install dependencies
- compile the Python files
- seed the database with initial data
- verify that `restaurant.create_app()` imports successfully

Push this folder to GitHub, and GitHub Actions will run automatically for `main` and `master` branches.

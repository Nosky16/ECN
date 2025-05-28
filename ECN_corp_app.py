from flask import Flask, render_template, request, redirect, session, g
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
import os

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'ecn_coop.db')

# Initialize the database with required tables
def init_db():
    print(f"Initializing database at {DATABASE}")
    with sqlite3.connect(DATABASE) as db:
        # Drop existing tables to ensure a clean slate (optional, for testing)
        db.execute('DROP TABLE IF EXISTS users')
        db.execute('DROP TABLE IF EXISTS savings')
        db.execute('DROP TABLE IF EXISTS loans')
        db.execute('DROP TABLE IF EXISTS loan_applications')
        db.execute('DROP TABLE IF EXISTS repayments')
        # Create tables
        db.execute('''CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        is_admin INTEGER NOT NULL DEFAULT 0
                    )''')
        print("Created users table")
        db.execute('''CREATE TABLE savings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        amount REAL,
                        date TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )''')
        print("Created savings table")
        db.execute('''CREATE TABLE loan_applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        type_of_loan TEXT,
                        amount REAL,
                        duration INTEGER,
                        ecn_staff_no TEXT,
                        ippis_no TEXT,
                        designation TEXT,
                        phone_no TEXT,
                        bank_name TEXT,
                        account_no TEXT,
                        previous_month_salary REAL,
                        guarantor1_name TEXT,
                        guarantor1_staff_no TEXT,
                        guarantor1_designation TEXT,
                        guarantor1_phone_no TEXT,
                        guarantor2_name TEXT,
                        guarantor2_staff_no TEXT,
                        guarantor2_designation TEXT,
                        guarantor2_phone_no TEXT,
                        date TEXT,
                        status TEXT DEFAULT 'pending',
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )''')
        print("Created loan_applications table")
        db.execute('''CREATE TABLE loans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        type_of_loan TEXT,
                        amount REAL,
                        duration INTEGER,
                        ecn_staff_no TEXT,
                        ippis_no TEXT,
                        designation TEXT,
                        phone_no TEXT,
                        bank_name TEXT,
                        account_no TEXT,
                        previous_month_salary REAL,
                        monthly_repayment REAL,
                        date TEXT,
                        status TEXT,
                        amount_approved REAL,
                        interest_charged REAL,
                        total_amount REAL,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )''')
        print("Created loans table")
        db.execute('''CREATE TABLE repayments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        loan_id INTEGER,
                        due_date TEXT,
                        amount REAL,
                        status INTEGER DEFAULT 0,  -- 0 for unpaid, 1 for paid
                        FOREIGN KEY (loan_id) REFERENCES loans(id)
                    )''')
        print("Created repayments table")
        # Insert sample data for testing
        db.execute('INSERT INTO users (name, is_admin) VALUES (?, ?)', ('TestUser', 0))
        db.execute('INSERT INTO users (name, is_admin) VALUES (?, ?)', ('AdminUser', 1))
        db.commit()
        print("Database initialization completed")

# Connect to SQLite database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

# Close DB connection after each request
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db:
        db.close()

# Call init_db when the app context is created
with app.app_context():
    init_db()  # Ensure the database is initialized

# Restrict access to logged-in users
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        db = get_db()
        cursor = db.execute('SELECT id, is_admin FROM users WHERE name=?', (name,))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            session['is_admin'] = user[1]
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='User not found. Please register first.')
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        # Check if is_admin is "on" (checkbox checked) or not
        is_admin = 1 if request.form.get('is_admin') == 'on' else 0
        db = get_db()
        try:
            cursor = db.execute('SELECT id FROM users WHERE name=?', (name,))
            if cursor.fetchone():
                return render_template('register.html', error='User already exists. Please log in.')
            db.execute('INSERT INTO users (name, is_admin) VALUES (?, ?)', (name, is_admin))
            db.commit()
            return redirect('/login')
        except sqlite3.Error as e:
            return render_template('register.html', error=f'Database error: {str(e)}')
    return render_template('register.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect('/login')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user_id = session['user_id']
    cursor = db.execute('SELECT name FROM users WHERE id=?', (user_id,))
    user = cursor.fetchone()
    if not user:
        session.clear()
        return redirect('/login')
    return render_template('dashboard.html', name=user[0], is_admin=session.get('is_admin'))

# Savings route
@app.route('/savings')
@login_required
def savings():
    db = get_db()
    user_id = session['user_id']
    cursor = db.execute('SELECT SUM(amount), date FROM savings WHERE user_id=? GROUP BY date', (user_id,))
    savings = cursor.fetchall()
    total = sum(amount for amount, _ in savings) if savings else 0
    return render_template('savings.html', total=total, savings=savings)

# Loan route
@app.route('/loan', methods=['GET', 'POST'])
@login_required
def loan():
    db = get_db()
    user_id = session['user_id']
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            duration = int(request.form['duration'])
            if amount <= 0 or duration <= 0:
                return render_template('loan.html', error='Amount and duration must be positive')
            # Collect form data
            type_of_loan = request.form['type_of_loan']
            ecn_staff_no = request.form['ecn_staff_no']
            ippis_no = request.form['ippis_no']
            designation = request.form['designation']
            phone_no = request.form['phone_no']
            bank_name = request.form['bank_name']
            account_no = request.form['account_no']
            previous_month_salary = float(request.form['previous_month_salary'])
            guarantor1_name = request.form['guarantor1_name']
            guarantor1_staff_no = request.form['guarantor1_staff_no']
            guarantor1_designation = request.form['guarantor1_designation']
            guarantor1_phone_no = request.form['guarantor1_phone_no']
            guarantor2_name = request.form['guarantor2_name']
            guarantor2_staff_no = request.form['guarantor2_staff_no']
            guarantor2_designation = request.form['guarantor2_designation']
            guarantor2_phone_no = request.form['guarantor2_phone_no']
            today = datetime.now().strftime('%Y-%m-%d')
            db.execute('''INSERT INTO loan_applications (
                            user_id, type_of_loan, amount, duration, ecn_staff_no, ippis_no, designation,
                            phone_no, bank_name, account_no, previous_month_salary, guarantor1_name,
                            guarantor1_staff_no, guarantor1_designation, guarantor1_phone_no,
                            guarantor2_name, guarantor2_staff_no, guarantor2_designation,
                            guarantor2_phone_no, date, status
                         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, type_of_loan, amount, duration, ecn_staff_no, ippis_no, designation,
                        phone_no, bank_name, account_no, previous_month_salary, guarantor1_name,
                        guarantor1_staff_no, guarantor1_designation, guarantor1_phone_no,
                        guarantor2_name, guarantor2_staff_no, guarantor2_designation,
                        guarantor2_phone_no, today, 'pending'))
            db.commit()
            return redirect('/loan')
        except ValueError as e:
            return render_template('loan.html', error='Invalid input: Ensure amounts and duration are numbers')
    cursor = db.execute('SELECT * FROM loan_applications WHERE user_id=? AND status="pending"', (user_id,))
    applications = cursor.fetchall()
    return render_template('loan.html', applications=applications)

# Repayments route
@app.route('/repayments')
@login_required
def repayments():
    db = get_db()
    user_id = session['user_id']
    cursor = db.execute('''
        SELECT r.id, r.due_date, r.amount, r.status
        FROM repayments r
        JOIN loans l ON r.loan_id = l.id
        WHERE l.user_id = ? AND l.status = "approved"
        ORDER BY r.due_date
    ''', (user_id,))
    repayments = cursor.fetchall()
    if not repayments:
        return render_template('repayments.html', repayments=[], error='No repayment schedule available.')
    return render_template('repayments.html', repayments=repayments)

# Mark repayment as paid
@app.route('/mark_paid/<int:repayment_id>')
@login_required
def mark_paid(repayment_id):
    db = get_db()
    user_id = session['user_id']
    cursor = db.execute('''
        SELECT r.id FROM repayments r
        JOIN loans l ON r.loan_id = l.id
        WHERE r.id = ? AND l.user_id = ?
    ''', (repayment_id, user_id))
    if cursor.fetchone():
        db.execute('UPDATE repayments SET status = 1 WHERE id = ?', (repayment_id,))
        db.commit()
    return redirect('/repayments')

# Admin dashboard route
@app.route('/admin')
@login_required
def admin():
    if not session.get('is_admin'):
        return redirect('/dashboard')
    return render_template('admin.html')

# Add savings route
@app.route('/add_savings', methods=['GET', 'POST'])
@login_required
def add_savings():
    if not session.get('is_admin'):
        return redirect('/dashboard')
    db = get_db()
    if request.method == 'POST':
        try:
            staff_id = int(request.form['staff_id'])
            amount = float(request.form['amount'])
            if amount <= 0:
                return render_template('add_savings.html', error='Amount must be positive')
            cursor = db.execute('SELECT id FROM users WHERE id = ?', (staff_id,))
            if not cursor.fetchone():
                return render_template('add_savings.html', error='Invalid Staff ID')
            db.execute('INSERT INTO savings (user_id, amount, date) VALUES (?, ?, ?)',
                       (staff_id, amount, datetime.now().strftime('%Y-%m-%d')))
            db.commit()
            return redirect('/add_savings')
        except ValueError:
            return render_template('add_savings.html', error='Invalid Staff ID or amount')
    cursor = db.execute('SELECT id, name FROM users WHERE is_admin = 0')
    users = cursor.fetchall()
    return render_template('add_savings.html', users=users)

# Users route
@app.route('/users')
@login_required
def users():
    if not session.get('is_admin'):
        return redirect('/dashboard')
    db = get_db()
    cursor = db.execute('SELECT id, name FROM users')
    users = cursor.fetchall()
    return render_template('users.html', users=users)

# Approve loans route
@app.route('/approve_loans')
@login_required
def approve_loans():
    if not session.get('is_admin'):
        return redirect('/dashboard')
    db = get_db()
    cursor = db.execute('SELECT id, user_id, amount, u.name FROM loan_applications l JOIN users u ON l.user_id = u.id WHERE l.status = "pending"')
    applications = cursor.fetchall()
    return render_template('approve_loans.html', applications=applications)

# Approve loan route
@app.route('/approve/<int:application_id>')
@login_required
def approve(application_id):
    if not session.get('is_admin'):
        return redirect('/dashboard')
    db = get_db()
    cursor = db.execute('SELECT * FROM loan_applications WHERE id = ?', (application_id,))
    application = cursor.fetchone()
    if application:
        user_id, type_of_loan, amount, duration, ecn_staff_no, ippis_no, designation, \
        phone_no, bank_name, account_no, previous_month_salary, guarantor1_name, \
        guarantor1_staff_no, guarantor1_designation, guarantor1_phone_no, guarantor2_name, \
        guarantor2_staff_no, guarantor2_designation, guarantor2_phone_no, date, status = application
        interest_charged = amount * 0.05
        monthly_repayment = (amount + interest_charged) / duration
        db.execute('''INSERT INTO loans (
                        user_id, type_of_loan, amount, duration, ecn_staff_no, ippis_no, designation,
                        phone_no, bank_name, account_no, previous_month_salary, monthly_repayment,
                        date, status, amount_approved, interest_charged, total_amount
                     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (user_id, type_of_loan, amount, duration, ecn_staff_no, ippis_no, designation,
                    phone_no, bank_name, account_no, previous_month_salary, monthly_repayment,
                    date, 'approved', amount, interest_charged, amount + interest_charged))
        loan_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        start_date = datetime.strptime(date, '%Y-%m-%d')
        for i in range(duration):
            due_date = (start_date + timedelta(days=30*i)).strftime('%Y-%m-%d')
            db.execute('INSERT INTO repayments (loan_id, due_date, amount, status) VALUES (?, ?, ?, ?)',
                       (loan_id, due_date, monthly_repayment, 0))
        db.execute('DELETE FROM loan_applications WHERE id = ?', (application_id,))
        db.commit()
    return redirect('/approve_loans')

# Loan approval details route
@app.route('/loan_approval_details/<int:loan_id>', methods=['GET', 'POST'])
@login_required
def loan_approval_details(loan_id):
    if not session.get('is_admin'):
        return redirect('/dashboard')
    db = get_db()
    cursor = db.execute('SELECT * FROM loans WHERE id = ?', (loan_id,))
    loan = cursor.fetchone()
    if request.method == 'POST':
        amount_approved = float(request.form['amount_approved'])
        interest_charged = float(request.form['interest_charged'])
        total_amount = float(request.form['total_amount'])
        monthly_repayment = total_amount / loan[4]  # duration
        db.execute('''UPDATE loans SET amount_approved = ?, interest_charged = ?, total_amount = ?, monthly_repayment = ?
                     WHERE id = ?''', (amount_approved, interest_charged, total_amount, monthly_repayment, loan_id))
        db.execute('DELETE FROM repayments WHERE loan_id = ?', (loan_id,))
        start_date = datetime.strptime(loan[14], '%Y-%m-%d')  # date
        for i in range(loan[4]):  # duration
            due_date = (start_date + timedelta(days=30*i)).strftime('%Y-%m-%d')
            db.execute('INSERT INTO repayments (loan_id, due_date, amount, status) VALUES (?, ?, ?, ?)',
                       (loan_id, due_date, monthly_repayment, 0))
        db.commit()
        return redirect('/approve_loans')
    return render_template('loan_approval_details.html', loan=loan)

if __name__ == '__main__':
    app.run(debug=True)

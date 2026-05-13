from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import os
import io
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'jobtracker_secret_key')

database_url = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jobs.db'))
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    jobs = db.relationship('Job', backref='user', lazy=True, cascade='all, delete-orphan')

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Applied')
    date_applied = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    status_filter = request.args.get('status', 'All')
    if status_filter == 'All':
        jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.date_applied.desc()).all()
    else:
        jobs = Job.query.filter_by(user_id=current_user.id, status=status_filter).order_by(Job.date_applied.desc()).all()
    counts = {
        'All': Job.query.filter_by(user_id=current_user.id).count(),
        'Applied': Job.query.filter_by(user_id=current_user.id, status='Applied').count(),
        'Interview': Job.query.filter_by(user_id=current_user.id, status='Interview').count(),
        'Offer': Job.query.filter_by(user_id=current_user.id, status='Offer').count(),
        'Rejected': Job.query.filter_by(user_id=current_user.id, status='Rejected').count(),
    }
    return render_template('dashboard.html', jobs=jobs, status_filter=status_filter, counts=counts)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_job():
    if request.method == 'POST':
        company = request.form.get('company')
        role = request.form.get('role')
        status = request.form.get('status', 'Applied')
        notes = request.form.get('notes', '')
        date_applied = request.form.get('date_applied')
        if date_applied:
            date_applied = date.fromisoformat(date_applied)
        else:
            date_applied = date.today()
        job = Job(company=company, role=role, status=status, notes=notes, date_applied=date_applied, user_id=current_user.id)
        db.session.add(job)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_job.html')

@app.route('/edit/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        job.company = request.form.get('company')
        job.role = request.form.get('role')
        job.status = request.form.get('status')
        job.notes = request.form.get('notes', '')
        date_applied = request.form.get('date_applied')
        if date_applied:
            job.date_applied = date.fromisoformat(date_applied)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_job.html', job=job)

@app.route('/delete/<int:job_id>')
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.user_id == current_user.id:
        db.session.delete(job)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('register'))
        hashed = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/status/<int:job_id>', methods=['POST'])
@login_required
def update_status(job_id):
    job = Job.query.get_or_404(job_id)
    if job.user_id == current_user.id:
        job.status = request.form.get('status')
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/export')
@login_required
def export():
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.date_applied.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Company', 'Role', 'Status', 'Date Applied', 'Notes'])
    for job in jobs:
        writer.writerow([job.company, job.role, job.status, job.date_applied, job.notes])
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=job_applications.csv'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

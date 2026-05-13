# Job Tracker

A full-stack web app for tracking job applications, built with Python and Flask. Deployed to production on Railway with PostgreSQL.

🔗 **[Live Demo](https://web-production-ad913.up.railway.app)**

## Features

- **User authentication** — register, log in, and log out securely
- **Add & manage jobs** — track company, role, status, date applied, and notes
- **Status tracking** — Applied, Interview, Offer, Rejected
- **Quick status update** — change a job's status directly from the dashboard
- **Search** — filter jobs by company or role name in real time
- **Sort** — sort by date applied, company, or status
- **Stats cards** — at-a-glance counts for each status
- **CSV export** — download all your applications as a spreadsheet

## Tech Stack

- Python 3 / Flask
- PostgreSQL via Flask-SQLAlchemy (SQLite for local development)
- Flask-Login for authentication
- Werkzeug for password hashing
- Bootstrap 5 for styling
- Deployed on Railway with Gunicorn

## Local Development

### 1. Install dependencies

```bash
pip install flask flask-sqlalchemy flask-login werkzeug gunicorn
```

### 2. Run the app

```bash
python app.py
```

Or double-click `run.bat` on Windows.

### 3. Open in browser

```
http://127.0.0.1:5000
```

Register an account and start tracking your applications.

## Deployment

The app is deployed on Railway. Environment variables required:

| Variable | Description |
|---|---|
| `SECRET_KEY` | A long random string for session security |
| `DATABASE_URL` | PostgreSQL connection string (set automatically by Railway) |

## Project Structure

```
Job_Tracker/
├── app.py               # Flask app, routes, and database models
├── Procfile             # Tells Railway how to start the app (gunicorn)
├── requirements.txt     # Python dependencies
├── run.bat              # Windows double-click launcher
└── templates/
    ├── base.html        # Shared layout and navigation
    ├── login.html       # Login page
    ├── register.html    # Registration page
    ├── dashboard.html   # Main job list with search, sort, and stats
    └── add_job.html     # Add and edit job form
```

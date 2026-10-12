# Expense Tracker

**Live demo:** https://expense-tracker-2amd.onrender.com

A full-stack expense tracker built with Flask. Create an account, track your spending, filter it, and see where your money goes.

## Features
- User accounts with register, login, and logout
- Each user sees only their own expenses
- Add, edit, and delete expenses
- Filter by category and month
- Total spending for the current filter
- Pie chart of spending by category
- Download expenses as a CSV file
- Form validation and flash messages
- Responsive layout with Bootstrap

## Built with
- Python and Flask
- Flask-SQLAlchemy and Flask-Login
- PostgreSQL (Neon) in production, SQLite locally
- Bootstrap and Chart.js
- Deployed on Render with Gunicorn

## Run it locally
```bash
git clone https://github.com/IRADUKUNDA-JULES/expense-tracker.git
cd expense-tracker
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000

Locally the app uses a SQLite file. To use Postgres instead, set the `DATABASE_URL` environment variable before running.

## Environment variables
| Name | Purpose |
|------|---------|
| `SECRET_KEY` | Signs session cookies |
| `DATABASE_URL` | Postgres connection string (optional locally) |

## Future improvements
- Monthly budgets with overspending warnings
- Password reset
- Database migrations with Flask-Migrate

## Author
Jules Iradukunda
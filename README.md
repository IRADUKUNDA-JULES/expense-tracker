# Expense Tracker

A simple expense tracker built with Flask and SQLite.

## Features
- Add, edit, and delete expenses
- Filter by category and month
- Total spending and a category pie chart
- Form validation and flash messages

## Run it locally
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000

## Built with
Python, Flask, Flask-SQLAlchemy, Bootstrap, Chart.js



**Live demo:** https://expense-tracker-2amd.onrender.com

Locally the app uses a SQLite file. To use Postgres instead, set the `DATABASE_URL` environment variable before running.

## Environment variables
| Name | Purpose |
|------|---------|
|`SECRET_KEY` | Signs flash message cookies |
|`DATABASE_URL` | Postgres connection string (optional locally) |



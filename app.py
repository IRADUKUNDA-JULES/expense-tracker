from flask import Flask, render_template, request, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "change -this-to-any-random-text"
uri = os.environ.get("DATABASE_URL", "sqlite:///expenses.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
if uri.startswith("postgresql://"):
    uri = uri.replace("postgresql://", "postgresql+psycopg2://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

with app.app_context():
    db.create_all()

def validate_expense(form):
    title = form.get("title", "").strip()
    category = form.get("category", "").strip()

    try:
        amount = float(form.get("amount", ""))
    except ValueError:
        return None, "Amount must be a number."

    if not title or not category:
        return None, "Title and category cannot be empty."
    if amount <= 0:
        return None, "Amount must be greater than zero."

    return (title, amount, category), None

@app.route("/")
@login_required
def home():
    category = request.args.get("category")
    month = request.args.get("month")  # format: 2026-10

    query = Expenses.query.filter_by(user_id=current_user.id)
    if category:
        query = query.filter(Expenses.category == category)
    if month:
        year, mon = map(int, month.split("-"))
        start = date(year, mon, 1)
        end = date(year + (mon == 12), mon % 12 + 1, 1)
        query = query.filter(Expenses.date >= start, Expenses.date < end)

    expenses = query.order_by(Expenses.date.desc()).all()
    total = sum(e.amount for e in expenses)
    category_totals = {}
    for e in expenses:
       category_totals[e.category] = category_totals.get(e.category, 0) + e.amount
    categories = [c[0] for c in db.session.query(Expenses.category).filter_by(user_id=current_user.id).distinct()]
    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        categories=categories,
        selected_category=category,
        selected_month=month,
        labels=list(category_totals.keys()),
        values=list(category_totals.values()),
    )

@app.route("/add", methods=["POST"])
@login_required
def add():
    data, error = validate_expense(request.form)
    if error:
        flash(error, "error")
        return redirect("/")

    title, amount, category = data
    db.session.add(Expenses(title=title, amount=amount, category=category, user_id=current_user.id))
    db.session.commit()
    flash("Expense added.", "success")
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    expense = Expenses.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET","POST"])
@login_required
def edit(id):
    expense = Expenses.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        data, error = validate_expense(request.form)
        if error:
            flash(error, "error")
            return redirect(request.url)

        expense.title, expense.amount, expense.category = data
        db.session.commit()
        flash("Expense updated.", "success")
        return redirect("/")
    return render_template("edit.html", expense=expense)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or len(password) < 6:
            flash("Enter a username and a password of at least 6 characters.", "error")
            return redirect("/register")
        if User.query.filter_by(username=username).first():
            flash("That username is taken.", "error")
            return redirect("/register")
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect("/")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"].strip()).first()
        if user and check_password_hash(user.password_hash, request.form["password"]):
            login_user(user)
            return redirect("/")
        flash("Wrong username or password.", "error")
        return redirect("/login")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)

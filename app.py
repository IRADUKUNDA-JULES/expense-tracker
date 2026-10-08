from flask import Flask, render_template, request, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import date

app = Flask(__name__)
app.secret_key = "change -this-to-any-random-text"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"
db = SQLAlchemy(app)

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=date.today)

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
def home():
    category = request.args.get("category")
    month = request.args.get("month")  # format: 2026-10

    query = Expenses.query
    if category:
        query = query.filter(Expenses.category == category)
    if month:
        query = query.filter(func.strftime("%Y-%m", Expenses.date) == month)

    expenses = query.order_by(Expenses.date.desc()).all()
    total = sum(e.amount for e in expenses)
    category_totals = {}
    for e in expenses:
       category_totals[e.category] = category_totals.get(e.category, 0) + e.amount
    categories = [c[0] for c in db.session.query(Expenses.category).distinct()]

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
def add():
    data, error = validate_expense(request.form)
    if error:
        flash(error, "error")
        return redirect("/")

    title, amount, category = data
    db.session.add(Expenses(title=title, amount=amount, category=category))
    db.session.commit()
    flash("Expense added.", "success")
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    expense = Expenses.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    expense = Expenses.query.get_or_404(id)
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


if __name__ == "__main__":
    app.run(debug=True)

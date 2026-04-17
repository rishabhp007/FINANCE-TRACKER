from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///finance.db")

@app.route("/")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = ?",
        session["user_id"]
    )

    balance = 0

    for t in transactions:
        if t["type"] == "income":
            balance += t["amount"]
        else:
            balance -= t["amount"]

    chart_data = db.execute("""
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE user_id = ? AND type='expense'
        GROUP BY category
    """, session["user_id"])

    categories = [row["category"] for row in chart_data]
    amounts = [row["total"] for row in chart_data]

    return render_template(
        "dashboard.html",
        balance=balance,
        transactions=transactions,
        categories=categories,
        amounts=amounts
    )


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        hash = generate_password_hash(password)

        db.execute(
        "INSERT INTO users (username, hash) VALUES (?,?)",
        username, hash)

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        rows = db.execute(
        "SELECT * FROM users WHERE username = ?",
        username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Invalid login"

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


@app.route("/income", methods=["GET","POST"])
def income():

    if request.method == "POST":

        category = request.form.get("source")
        amount = request.form.get("amount")
        description = request.form.get("description")

        db.execute(
        "INSERT INTO transactions (user_id,type,source,amount,description) VALUES (?,?,?,?,?)",
        session["user_id"],
        "income",
        source,
        amount,
        description
        )

        return redirect("/")

    return render_template("add_income.html")


@app.route("/expense", methods=["GET","POST"])
def expense():

    if request.method == "POST":

        category = request.form.get("category")
        amount = request.form.get("amount")
        description = request.form.get("description")

        db.execute(
        "INSERT INTO transactions (user_id,type,category,amount,description) VALUES (?,?,?,?,?)",
        session["user_id"],
        "expense",
        category,
        amount,
        description
        )

        return redirect("/")

    return render_template("add_expense.html")


@app.route("/history")
def history():

    transactions = db.execute(
    "SELECT * FROM transactions WHERE user_id = ?",
    session["user_id"]
    )

    return render_template("history.html", transactions=transactions)


if __name__ == "__main__":
    app.run(debug=True)
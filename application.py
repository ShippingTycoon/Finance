import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")

        quote = lookup(symbol)

        # Check for correct symbol input
        if not symbol or not quote:
            return apology("Provide a valid stock symbol")

        row = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session.get("user_id"))

        cash = float(row[0]['cash'])

        price = quote['price']

        # Check the user has enough cash
        if cash < price:
            return apology("You dont have enough money to make this transaction")

        shares = request.form.get("shares")

        # Check for corerct format of shares input
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("Provide positive integer for shares you wish to purchase")

        # Insert record of purchase into purchases table
        else:
            db.execute("INSERT INTO purchases (user_id, symbol, price) VALUES (:user_id, :symbol, :price)",
            user_id = session.get("user_id"), symbol = symbol, price = price)
            return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        symbol = request.form.get("symbol")

        # Ensure stock symbol was submitted
        if not symbol:
            return apology("must provide stock symbol")
        else:
            # Call lookup function to find stock information
            quote = lookup(symbol)

            # Check for response
            if quote == None:
                return apology("The symbol you entered does not exist")

            # Pass returned variables into quoted.html and redirect
            else:
                return render_template("quoted.html", name = quote['name'], symbol = quote['symbol'], price = usd(quote['price']))

    # Load quote.html
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirmation of password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password", 403)

        # Check for discrepancies between password and confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        # Query database for username & check if already taken
        username = request.form.get("username")
        profile = db.execute("SELECT username FROM users WHERE username = :username", username=username)
        if username == profile:
            return apology("username already taken")

        # Enter username and password into users database
        else:
            password = request.form.get("password")
            hashed_password = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashed_password)",
            username=username, hashed_password=hashed_password)
            # Take user to login page
            return redirect("/login")

    # Take user to register.html
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

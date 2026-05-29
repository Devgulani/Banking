from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

import db
from auth import (
    authenticate_user,
    create_user,
    current_user,
    login_required,
    login_user,
    logout_user,
    validate_email,
    validate_password,
    validate_username,
)
from db import get_db


NAV_ITEMS = [
    {"label": "Overview", "icon": "OV", "endpoint": "dashboard", "slug": "overview"},
    {"label": "Transactions", "icon": "TX", "endpoint": "transactions", "slug": "transactions"},
    {"label": "Transfer", "icon": "TR", "endpoint": "transfer", "slug": "transfer"},
    {"label": "Cards", "icon": "CD", "endpoint": "cards", "slug": "cards"},
    {"label": "Analytics", "icon": "AN", "endpoint": "analytics", "slug": "analytics"},
    {"label": "Support", "icon": "SP", "endpoint": "support", "slug": "support"},
    {"label": "Profile", "icon": "PF", "endpoint": "profile", "slug": "profile"},
    {"label": "Notifications", "icon": "NT", "endpoint": "notifications", "slug": "notifications"},
]

QUICK_ACTIONS = [
    {"label": "Transfer", "description": "Send money instantly", "icon": "TR", "endpoint": "transfer", "slug": "transfer"},
    {"label": "Cards", "description": "Freeze and set limits", "icon": "CD", "endpoint": "cards", "slug": "cards"},
    {"label": "Analytics", "description": "Review monthly trends", "icon": "AN", "endpoint": "analytics", "slug": "analytics"},
    {"label": "History", "description": "Search all transactions", "icon": "TX", "endpoint": "transactions", "slug": "transactions"},
    {"label": "Profile", "description": "Update preferences", "icon": "PF", "endpoint": "profile", "slug": "profile"},
    {"label": "Support", "description": "Chat with us 24/7", "icon": "SP", "endpoint": "support", "slug": "support"},
]


def make_account(user: dict) -> dict:
    balance = float(user["balance"])
    return {
        "id": user["id"],
        "holder": user["username"],
        "email": user["email"],
        "name": "Everyday Account",
        "number_masked": f"**** {int(user['id']):04d}",
        "balance": balance,
        "available": balance,
        "currency": "Rs.",
    }


def get_user_transactions(user_id: int) -> list[dict]:
    rows = get_db().execute(
        """
        SELECT id, description, category, amount, type, created_at
        FROM transactions
        WHERE user_id = ?
        ORDER BY datetime(created_at) DESC, id DESC
        """,
        (user_id,),
    ).fetchall()
    return [
        {
            "id": f"tx-{row['id']}",
            "description": row["description"],
            "category": row["category"],
            "date": row["created_at"][:10],
            "amount": float(row["amount"]),
            "type": row["type"],
        }
        for row in rows
    ]


def dashboard_context(active_nav: str = "overview") -> dict:
    user = current_user()
    account = make_account(user)
    transactions = get_user_transactions(user["id"])
    categories = sorted({tx["category"] for tx in transactions}) or ["Income", "Transfer"]
    nav_items = [{**item, "href": url_for(item["endpoint"])} for item in NAV_ITEMS]
    quick_actions = [{**action, "href": url_for(action["endpoint"])} for action in QUICK_ACTIONS]
    return {
        "account": account,
        "transactions": transactions,
        "categories": categories,
        "quick_actions": quick_actions,
        "nav_items": nav_items,
        "active_nav": active_nav,
    }


def validate_signup_form(form) -> tuple[dict, str | None]:
    username = (form.get("username") or "").strip()
    email = (form.get("email") or "").strip().lower()
    account_number = (form.get("account_number") or "").strip()
    password = form.get("password") or ""
    confirm_password = form.get("confirm_password") or ""

    error = (
        validate_username(username)
        or validate_email(email)
        or ("Account number must be numeric only." if not account_number.isdigit() else "")
        or validate_password(password)
        or ("Passwords do not match." if password != confirm_password else "")
    )
    return {
        "username": username,
        "email": email,
        "account_number": account_number,
        "password": password,
    }, error or None


def validate_login_form(form) -> tuple[dict, str | None]:
    username = (form.get("username") or "").strip()
    password = form.get("password") or ""
    error = validate_username(username) or validate_password(password, strong=False)
    return {"username": username, "password": password}, error or None


def create_transfer(sender: dict, receiver_id: int, amount: float, remarks: str) -> str | None:
    if receiver_id == sender["id"]:
        return "Choose a different receiver account."
    if amount <= 0:
        return "Transfer amount must be greater than zero."
    if amount > float(sender["balance"]):
        return "Transfer amount exceeds your available balance."

    conn = get_db()
    receiver = conn.execute("SELECT * FROM users WHERE id = ?", (receiver_id,)).fetchone()
    if receiver is None:
        return "Receiver account was not found."

    cursor = conn.execute(
        """
        INSERT INTO transfers (sender_id, receiver_id, amount, remarks)
        VALUES (?, ?, ?, ?)
        """,
        (sender["id"], receiver_id, amount, remarks),
    )
    transfer_id = cursor.lastrowid
    conn.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, sender["id"]))
    conn.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, receiver_id))
    conn.execute(
        """
        INSERT INTO transactions (user_id, transfer_id, description, category, amount, type)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (sender["id"], transfer_id, f"Transfer to {receiver['username']}", "Transfer", -amount, "debit"),
    )
    conn.execute(
        """
        INSERT INTO transactions (user_id, transfer_id, description, category, amount, type)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (receiver_id, transfer_id, f"Transfer from {sender['username']}", "Transfer", amount, "credit"),
    )
    conn.commit()
    return None


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = os.getenv("DATABASE", os.path.join(app.instance_path, "banking.sqlite3"))
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    db.init_app(app)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", **dashboard_context("overview"))

    @app.route("/transfer", methods=["GET", "POST"])
    @login_required
    def transfer():
        error = None
        success = None
        if request.method == "POST":
            sender = current_user()
            receiver_raw = (request.form.get("receiver") or "").strip()
            amount_raw = (request.form.get("amount") or "").strip()
            remarks = (request.form.get("remarks") or "").strip()

            if not receiver_raw.isdigit():
                error = "Receiver account must be numeric."
            else:
                try:
                    amount = float(amount_raw)
                except ValueError:
                    amount = 0
                error = create_transfer(sender, int(receiver_raw), amount, remarks)
                if error is None:
                    success = "Transfer completed successfully."

        return render_template("transfer.html", error=error, success=success, **dashboard_context("transfer"))

    @app.get("/cards")
    @login_required
    def cards():
        return render_template("cards.html", **dashboard_context("cards"))

    @app.get("/analytics")
    @login_required
    def analytics():
        return render_template("analytics.html", **dashboard_context("analytics"))

    @app.get("/support")
    @login_required
    def support():
        return render_template("support.html", **dashboard_context("support"))

    @app.get("/profile")
    @login_required
    def profile():
        return render_template("profile.html", **dashboard_context("profile"))

    @app.get("/notifications")
    @login_required
    def notifications():
        return render_template("notifications.html", **dashboard_context("notifications"))

    @app.get("/transactions")
    @login_required
    def transactions():
        return render_template("transactions.html", **dashboard_context("transactions"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user() is not None:
            return redirect(url_for("dashboard"))

        error = None
        if request.method == "POST":
            data, error = validate_login_form(request.form)
            if error is None:
                user, error = authenticate_user(data["username"], data["password"])
                if user is not None:
                    login_user(user, remember=bool(request.form.get("remember")))
                    return redirect(url_for("dashboard"))

        return render_template("login.html", error=error, success=None)

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user() is not None:
            return redirect(url_for("dashboard"))

        error = None
        success = None
        customer_id = None
        if request.method == "POST":
            data, error = validate_signup_form(request.form)
            if error is None:
                user, error = create_user(data["username"], data["email"], data["password"])
                if user is not None:
                    customer_id = f"AXER-{int(user['id']):04d}"
                    success = "Account created. You can now sign in."

        return render_template("signup.html", error=error, success=success, customer_id=customer_id)

    @app.get("/logout")
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.get("/health")
    def health():
        return jsonify(status="ok", time=datetime.now(timezone.utc).isoformat())

    @app.route("/api/echo", methods=["GET", "POST"])
    def echo():
        msg = request.args.get("msg")
        if msg is None and request.is_json:
            payload = request.get_json(silent=True) or {}
            msg = payload.get("msg")
        return jsonify(msg=msg, method=request.method)

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") not in {"0", "false", "False"}
    app.run(host=host, port=port, debug=debug)

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, redirect, render_template, request, url_for

# Demo banking data - replace with database queries in production.
DEMO_ACCOUNT = {
    "holder": "Anu Sharma",
    "name": "Everyday Account",
    "number_masked": "**** 4821",
    "balance": 128_450.25,
    "available": 125_200.00,
    "currency": "Rs.",
}

DEMO_TRANSACTIONS = [
    {
        "id": "tx-001",
        "description": "Salary - Acme Corp",
        "category": "Income",
        "date": "2026-05-27",
        "amount": 75_000.00,
        "type": "credit",
    },
    {
        "id": "tx-002",
        "description": "Rent - Maple Apartments",
        "category": "Housing",
        "date": "2026-05-26",
        "amount": -28_000.00,
        "type": "debit",
    },
    {
        "id": "tx-003",
        "description": "Swiggy",
        "category": "Food",
        "date": "2026-05-25",
        "amount": -680.50,
        "type": "debit",
    },
    {
        "id": "tx-004",
        "description": "Amazon Pay",
        "category": "Shopping",
        "date": "2026-05-24",
        "amount": -2_499.00,
        "type": "debit",
    },
    {
        "id": "tx-005",
        "description": "UPI - Rahul K.",
        "category": "Transfer",
        "date": "2026-05-23",
        "amount": 5_000.00,
        "type": "credit",
    },
    {
        "id": "tx-006",
        "description": "BigBasket",
        "category": "Groceries",
        "date": "2026-05-22",
        "amount": -2_180.00,
        "type": "debit",
    },
]

DEMO_NAV_ITEMS = [
    {"label": "Overview", "icon": "OV", "endpoint": "dashboard", "slug": "overview"},
    {"label": "Transactions", "icon": "TX", "endpoint": "transactions", "slug": "transactions"},
    {"label": "Transfer", "icon": "TR", "endpoint": "transfer", "slug": "transfer"},
    {"label": "Cards", "icon": "CD", "endpoint": "cards", "slug": "cards"},
    {"label": "Analytics", "icon": "AN", "endpoint": "analytics", "slug": "analytics"},
    {"label": "Support", "icon": "SP", "endpoint": "support", "slug": "support"},
    {"label": "Profile", "icon": "PF", "endpoint": "profile", "slug": "profile"},
    {"label": "Notifications", "icon": "NT", "endpoint": "notifications", "slug": "notifications"},
]

DEMO_QUICK_ACTIONS = [
    {"label": "Transfer", "description": "Send money instantly", "icon": "TR", "endpoint": "transfer", "slug": "transfer"},
    {"label": "Cards", "description": "Freeze and set limits", "icon": "CD", "endpoint": "cards", "slug": "cards"},
    {"label": "Analytics", "description": "Review monthly trends", "icon": "AN", "endpoint": "analytics", "slug": "analytics"},
    {"label": "History", "description": "Search all transactions", "icon": "TX", "endpoint": "transactions", "slug": "transactions"},
    {"label": "Profile", "description": "Update preferences", "icon": "PF", "endpoint": "profile", "slug": "profile"},
    {"label": "Support", "description": "Chat with us 24/7", "icon": "SP", "endpoint": "support", "slug": "support"},
]


def dashboard_context(active_nav: str = "overview") -> dict:
    nav_items = [
        {
            **item,
            "href": url_for(item["endpoint"]),
        }
        for item in DEMO_NAV_ITEMS
    ]
    quick_actions = [
        {
            **action,
            "href": url_for(action["endpoint"]),
        }
        for action in DEMO_QUICK_ACTIONS
    ]
    return {
        "account": DEMO_ACCOUNT,
        "transactions": DEMO_TRANSACTIONS,
        "categories": sorted({tx["category"] for tx in DEMO_TRANSACTIONS}),
        "quick_actions": quick_actions,
        "nav_items": nav_items,
        "active_nav": active_nav,
    }


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/dashboard")
    def dashboard():
        return render_template("dashboard.html", **dashboard_context("overview"))

    @app.get("/transfer")
    def transfer():
        return render_template("transfer.html", **dashboard_context("transfer"))

    @app.get("/cards")
    def cards():
        return render_template("cards.html", **dashboard_context("cards"))

    @app.get("/analytics")
    def analytics():
        return render_template("analytics.html", **dashboard_context("analytics"))

    @app.get("/support")
    def support():
        return render_template("support.html", **dashboard_context("support"))

    @app.get("/profile")
    def profile():
        return render_template("profile.html", **dashboard_context("profile"))

    @app.get("/notifications")
    def notifications():
        return render_template("notifications.html", **dashboard_context("notifications"))

    @app.get("/transactions")
    def transactions():
        return render_template("transactions.html", **dashboard_context("transactions"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        success = None

        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            if not username or not password:
                error = "Please enter both a username and password."
            else:
                return redirect(url_for("dashboard"))

        return render_template("login.html", error=error, success=success)

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        error = None
        success = None
        customer_id = None

        if request.method == "POST":
            account_number = (request.form.get("account_number") or "").strip()

            if not account_number:
                error = "Please enter your account number."
            else:
                # Demo behavior only: in a real app you'd validate the account number
                # and persist a customer record in a database.
                customer_id = str(uuid.uuid4())
                success = "Account created (demo). Your customer ID is below."

        return render_template(
            "signup.html",
            error=error,
            success=success,
            customer_id=customer_id,
        )

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            time=datetime.now(timezone.utc).isoformat(),
        )

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

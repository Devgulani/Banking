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
    {"label": "Overview", "icon": "OV", "href": "#overview", "slug": "overview"},
    {"label": "Transactions", "icon": "TX", "href": "#transactions", "slug": "transactions"},
    {"label": "Quick actions", "icon": "QA", "href": "#quick-actions", "slug": "actions"},
    {"label": "Analytics", "icon": "AN", "href": "#dashboard-analytics", "slug": "analytics"},
    {"label": "Statements", "icon": "ST", "href": "#transactions", "slug": "statements"},
]

DEMO_QUICK_ACTIONS = [
    {"label": "Transfer", "description": "Send money instantly", "icon": "TR", "slug": "transfer"},
    {"label": "Pay bills", "description": "Utilities and recharges", "icon": "PB", "slug": "bills"},
    {"label": "Deposit", "description": "Add funds via UPI", "icon": "DP", "slug": "deposit"},
    {"label": "Cards", "description": "Freeze and set limits", "icon": "CD", "slug": "cards"},
    {"label": "Statements", "description": "Download PDF", "icon": "ST", "slug": "statements"},
    {"label": "Support", "description": "Chat with us 24/7", "icon": "SP", "slug": "support"},
]


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/dashboard")
    def dashboard():
        return render_template(
            "dashboard.html",
            account=DEMO_ACCOUNT,
            transactions=DEMO_TRANSACTIONS,
            categories=sorted({tx["category"] for tx in DEMO_TRANSACTIONS}),
            quick_actions=DEMO_QUICK_ACTIONS,
            nav_items=DEMO_NAV_ITEMS,
            active_nav="overview",
        )

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

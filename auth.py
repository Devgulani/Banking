from __future__ import annotations

import re
from functools import wraps

from flask import redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db


USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{5,}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_username(username: str) -> str:
    if not username:
        return "Username is required."
    if len(username) < 5:
        return "Username must be at least 5 characters."
    if not USERNAME_RE.fullmatch(username):
        return "Username may contain only letters, numbers, and underscores."
    return ""


def validate_email(email: str) -> str:
    if not email:
        return "Email is required."
    if not EMAIL_RE.fullmatch(email):
        return "Enter a valid email address."
    return ""


def validate_password(password: str, *, strong: bool = True) -> str:
    if not password:
        return "Password is required."
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if strong and not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if strong and not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if strong and not re.search(r"\d", password):
        return "Password must contain at least one number."
    if strong and not re.search(r"[^A-Za-z0-9]", password):
        return "Password must contain at least one special character."
    return ""


def create_user(username: str, email: str, password: str, starting_balance: float = 10000.0) -> tuple[dict | None, str | None]:
    db = get_db()
    existing = db.execute(
        """
        SELECT id, username, email
        FROM users
        WHERE lower(username) = lower(?) OR lower(email) = lower(?)
        """,
        (username, email),
    ).fetchone()
    if existing and existing["username"].lower() == username.lower():
        return None, "That username is already taken."
    if existing and existing["email"].lower() == email.lower():
        return None, "That email is already registered."

    password_hash = generate_password_hash(password)
    cursor = db.execute(
        """
        INSERT INTO users (username, email, password_hash, balance)
        VALUES (?, ?, ?, ?)
        """,
        (username, email, password_hash, starting_balance),
    )
    user_id = cursor.lastrowid
    db.execute(
        """
        INSERT INTO transactions (user_id, description, category, amount, type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, "Welcome deposit", "Income", starting_balance, "credit"),
    )
    db.commit()
    return get_user_by_id(user_id), None


def authenticate_user(username: str, password: str) -> tuple[dict | None, str | None]:
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    if user is None or not check_password_hash(user["password_hash"], password):
        return None, "Invalid username or password."
    return dict(user), None


def get_user_by_id(user_id: int) -> dict | None:
    row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def login_user(user: dict, remember: bool = False) -> None:
    session.clear()
    session["user_id"] = user["id"]
    session.permanent = remember


def logout_user() -> None:
    session.clear()


def current_user() -> dict | None:
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return get_user_by_id(int(user_id))


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view

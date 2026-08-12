"""
routes/auth.py — signup / login / logout / session check.

Passwords are hashed with werkzeug's generate_password_hash (never stored
in plain text). A session is just a random token saved in the `sessions`
table against the user's id — the browser keeps that token in
localStorage and sends it back as `Authorization: Bearer <token>`.
"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime, timezone

from db import get_db

auth_bp = Blueprint("auth", __name__)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_user_from_token(token):
    if not token:
        return None
    conn = get_db()
    row = conn.execute(
        "SELECT users.* FROM sessions JOIN users ON sessions.user_id = users.id "
        "WHERE sessions.token = ?",
        (token,),
    ).fetchone()
    conn.close()
    return row


def get_token_from_request():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:]
    return None


def require_auth():
    """Returns the user row for the current request, or None."""
    token = get_token_from_request()
    return get_user_from_token(token)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if len(username) < 3:
        return jsonify(error="Username should be at least 3 letters."), 400
    if len(password) < 4:
        return jsonify(error="Password should be at least 4 characters."), 400

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify(error="That name is already taken in this room."), 409

    user_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (user_id, username, generate_password_hash(password), now_iso()),
    )

    token = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
        (token, user_id, now_iso()),
    )
    conn.commit()
    conn.close()

    return jsonify(token=token, user={"id": user_id, "username": username})


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        conn.close()
        return jsonify(error="That name and password don't match anything here."), 401

    token = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
        (token, user["id"], now_iso()),
    )
    conn.commit()
    conn.close()

    return jsonify(token=token, user={"id": user["id"], "username": user["username"]})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    token = get_token_from_request()
    if token:
        conn = get_db()
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
    return jsonify(ok=True)


@auth_bp.route("/me", methods=["GET"])
def me():
    user = require_auth()
    if not user:
        return jsonify(user=None), 401
    return jsonify(user={"id": user["id"], "username": user["username"]})

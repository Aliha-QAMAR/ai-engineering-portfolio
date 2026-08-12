"""
routes/journals.py — diary entries with a visibility setting.

visibility is one of: 'private', 'public', 'penpals'
  - private  -> only the author sees it
  - public   -> shows up in everyone's public "book"
  - penpals  -> only shows up for the author's accepted pen pals
"""
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from db import get_db
from routes.auth import require_auth

journals_bp = Blueprint("journals", __name__)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def serialize(row, include_author=False):
    data = {
        "id": row["id"],
        "title": row["title"],
        "topic": row["topic"],
        "body": row["body"],
        "visibility": row["visibility"],
        "created_at": row["created_at"],
    }
    if include_author:
        data["author"] = row["author_username"] if "author_username" in row.keys() else None
    return data


@journals_bp.route("", methods=["POST"])
def create_journal():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "Untitled entry").strip()
    topic = (data.get("topic") or "").strip() or None
    body = (data.get("body") or "").strip()
    visibility = data.get("visibility") or "private"

    if visibility not in ("private", "public", "penpals"):
        visibility = "private"
    if not body:
        return jsonify(error="A blank page isn't a journal entry yet."), 400

    journal_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute(
        "INSERT INTO journals (id, owner_id, title, topic, body, visibility, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (journal_id, user["id"], title, topic, body, visibility, now_iso()),
    )
    conn.commit()
    conn.close()

    return jsonify(ok=True, id=journal_id)


@journals_bp.route("/mine", methods=["GET"])
def my_journals():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM journals WHERE owner_id = ? ORDER BY created_at DESC", (user["id"],)
    ).fetchall()
    conn.close()
    return jsonify(journals=[serialize(r) for r in rows])


@journals_bp.route("/public", methods=["GET"])
def public_journals():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    rows = conn.execute("""
        SELECT journals.*, users.username as author_username
        FROM journals JOIN users ON users.id = journals.owner_id
        WHERE journals.visibility = 'public'
        ORDER BY journals.created_at DESC
        LIMIT 200
    """).fetchall()
    conn.close()
    return jsonify(journals=[serialize(r, include_author=True) for r in rows])


@journals_bp.route("/penpals", methods=["GET"])
def penpal_journals():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    rows = conn.execute("""
        SELECT journals.*, users.username as author_username
        FROM journals
        JOIN users ON users.id = journals.owner_id
        JOIN penpals ON penpals.penpal_id = journals.owner_id
        WHERE journals.visibility = 'penpals' AND penpals.user_id = ?
        ORDER BY journals.created_at DESC
    """, (user["id"],)).fetchall()
    conn.close()
    return jsonify(journals=[serialize(r, include_author=True) for r in rows])

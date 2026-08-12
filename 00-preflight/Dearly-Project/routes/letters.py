"""
routes/letters.py — the inbox.

A letter has a `kind`:
  - 'penpal'    -> sent to (or from) someone who is an accepted pen pal.
                   Shown with a flower on the frontend.
  - 'anonymous' -> dropped in a bottle, drifts to a random other person
                   in the room. Shown as a sealed bottle on the frontend,
                   and the sender's identity is never revealed to the
                   recipient in the API response (even though we keep it
                   internally so a reply can find its way back).
"""
import uuid
import random
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from db import get_db
from routes.auth import require_auth

letters_bp = Blueprint("letters", __name__)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def serialize(row, viewer_id):
    """Hide the sender's identity for anonymous letters."""
    data = {
        "id": row["id"],
        "body": row["body"],
        "kind": row["kind"],
        "mood": row["mood"],
        "opened": bool(row["opened"]),
        "created_at": row["created_at"],
        "is_mine_to_read": row["owner_id"] == viewer_id,
    }
    if row["kind"] == "penpal" and row["from_username"]:
        data["from"] = row["from_username"]
    else:
        data["from"] = None
    return data


@letters_bp.route("/inbox", methods=["GET"])
def inbox():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    rows = conn.execute("""
        SELECT letters.*, users.username as from_username
        FROM letters
        LEFT JOIN users ON users.id = letters.from_id
        WHERE letters.owner_id = ?
        ORDER BY letters.created_at DESC
    """, (user["id"],)).fetchall()
    conn.close()

    return jsonify(letters=[serialize(r, user["id"]) for r in rows])


@letters_bp.route("/send", methods=["POST"])
def send_letter():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    data = request.get_json(silent=True) or {}
    to_username = (data.get("to") or "").strip()
    body = (data.get("body") or "").strip()
    mood = (data.get("mood") or "").strip() or None

    if not body:
        return jsonify(error="A letter needs some words in it."), 400

    conn = get_db()

    if to_username:
        # must be an accepted pen pal
        recipient = conn.execute(
            "SELECT * FROM users WHERE username = ?", (to_username,)
        ).fetchone()
        if not recipient:
            conn.close()
            return jsonify(error="No one by that name here."), 404
        is_penpal = conn.execute(
            "SELECT 1 FROM penpals WHERE user_id = ? AND penpal_id = ?",
            (user["id"], recipient["id"]),
        ).fetchone()
        if not is_penpal:
            conn.close()
            return jsonify(error="You can only address a letter to a pen pal you've already connected with."), 400
        owner_id = recipient["id"]
        kind = "penpal"
    else:
        # anonymous — drifts to a random other person in the room
        candidates = conn.execute(
            "SELECT id FROM users WHERE id != ?", (user["id"],)
        ).fetchall()
        if not candidates:
            conn.close()
            return jsonify(error="No one else is in the room yet for a bottle to drift to."), 400
        owner_id = random.choice(candidates)["id"]
        kind = "anonymous"

    letter_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO letters (id, owner_id, from_id, to_label, body, kind, mood, opened, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (letter_id, owner_id, user["id"], to_username or None, body, kind, mood, now_iso()),
    )
    conn.commit()
    conn.close()

    return jsonify(ok=True, id=letter_id)


@letters_bp.route("/<letter_id>/open", methods=["POST"])
def open_letter(letter_id):
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    row = conn.execute(
        "SELECT letters.*, users.username as from_username FROM letters "
        "LEFT JOIN users ON users.id = letters.from_id "
        "WHERE letters.id = ? AND letters.owner_id = ?",
        (letter_id, user["id"]),
    ).fetchone()
    if not row:
        conn.close()
        return jsonify(error="That letter isn't in your tray."), 404

    conn.execute("UPDATE letters SET opened = 1 WHERE id = ?", (letter_id,))
    conn.commit()
    conn.close()

    fresh = dict(row)
    fresh["opened"] = 1
    return jsonify(letter=serialize(fresh, user["id"]))


@letters_bp.route("/<letter_id>/reply", methods=["POST"])
def reply_letter(letter_id):
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    data = request.get_json(silent=True) or {}
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify(error="Write something before sealing your reply."), 400

    conn = get_db()
    original = conn.execute(
        "SELECT * FROM letters WHERE id = ? AND owner_id = ?", (letter_id, user["id"])
    ).fetchone()
    if not original:
        conn.close()
        return jsonify(error="Can't find that letter to reply to."), 404
    if not original["from_id"]:
        conn.close()
        return jsonify(error="This letter has no return address."), 400

    reply_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO letters (id, owner_id, from_id, to_label, body, kind, mood, opened, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (reply_id, original["from_id"], user["id"], None, body, original["kind"], None, now_iso()),
    )
    conn.commit()
    conn.close()

    return jsonify(ok=True, id=reply_id)

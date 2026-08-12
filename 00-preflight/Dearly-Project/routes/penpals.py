"""
routes/penpals.py — finding and connecting with pen pals.
"""
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from db import get_db
from routes.auth import require_auth

penpals_bp = Blueprint("penpals", __name__)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


@penpals_bp.route("/search", methods=["GET"])
def search():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify(results=[])

    conn = get_db()
    rows = conn.execute(
        "SELECT id, username FROM users WHERE username LIKE ? AND id != ? LIMIT 20",
        (f"%{q}%", user["id"]),
    ).fetchall()

    results = []
    for r in rows:
        is_penpal = conn.execute(
            "SELECT 1 FROM penpals WHERE user_id = ? AND penpal_id = ?", (user["id"], r["id"])
        ).fetchone()
        pending = conn.execute(
            "SELECT 1 FROM penpal_requests WHERE from_id = ? AND to_id = ? AND status = 'pending'",
            (user["id"], r["id"]),
        ).fetchone()
        results.append({
            "username": r["username"],
            "is_penpal": bool(is_penpal),
            "request_pending": bool(pending),
        })
    conn.close()
    return jsonify(results=results)


@penpals_bp.route("/request", methods=["POST"])
def send_request():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    data = request.get_json(silent=True) or {}
    to_username = (data.get("to") or "").strip()

    conn = get_db()
    target = conn.execute("SELECT * FROM users WHERE username = ?", (to_username,)).fetchone()
    if not target:
        conn.close()
        return jsonify(error="No one by that name here."), 404
    if target["id"] == user["id"]:
        conn.close()
        return jsonify(error="You can't send a request to yourself."), 400

    already = conn.execute(
        "SELECT 1 FROM penpals WHERE user_id = ? AND penpal_id = ?", (user["id"], target["id"])
    ).fetchone()
    if already:
        conn.close()
        return jsonify(error="You're already pen pals."), 400

    pending = conn.execute(
        "SELECT 1 FROM penpal_requests WHERE from_id = ? AND to_id = ? AND status = 'pending'",
        (user["id"], target["id"]),
    ).fetchone()
    if pending:
        conn.close()
        return jsonify(error="You already sent a request — waiting for them to answer."), 400

    req_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO penpal_requests (id, from_id, to_id, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
        (req_id, user["id"], target["id"], now_iso()),
    )
    conn.commit()
    conn.close()
    return jsonify(ok=True, id=req_id)


@penpals_bp.route("/requests/incoming", methods=["GET"])
def incoming_requests():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    rows = conn.execute("""
        SELECT penpal_requests.id, users.username as from_username, penpal_requests.created_at
        FROM penpal_requests JOIN users ON users.id = penpal_requests.from_id
        WHERE penpal_requests.to_id = ? AND penpal_requests.status = 'pending'
        ORDER BY penpal_requests.created_at DESC
    """, (user["id"],)).fetchall()
    conn.close()
    return jsonify(requests=[dict(r) for r in rows])


@penpals_bp.route("/requests/outgoing", methods=["GET"])
def outgoing_requests():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    rows = conn.execute("""
        SELECT penpal_requests.id, users.username as to_username, penpal_requests.created_at
        FROM penpal_requests JOIN users ON users.id = penpal_requests.to_id
        WHERE penpal_requests.from_id = ? AND penpal_requests.status = 'pending'
        ORDER BY penpal_requests.created_at DESC
    """, (user["id"],)).fetchall()
    conn.close()
    return jsonify(requests=[dict(r) for r in rows])


@penpals_bp.route("/requests/<req_id>/accept", methods=["POST"])
def accept_request(req_id):
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    req = conn.execute(
        "SELECT * FROM penpal_requests WHERE id = ? AND to_id = ? AND status = 'pending'",
        (req_id, user["id"]),
    ).fetchone()
    if not req:
        conn.close()
        return jsonify(error="Can't find that request."), 404

    conn.execute("UPDATE penpal_requests SET status = 'accepted' WHERE id = ?", (req_id,))
    conn.execute(
        "INSERT OR IGNORE INTO penpals (user_id, penpal_id, created_at) VALUES (?, ?, ?)",
        (user["id"], req["from_id"], now_iso()),
    )
    conn.execute(
        "INSERT OR IGNORE INTO penpals (user_id, penpal_id, created_at) VALUES (?, ?, ?)",
        (req["from_id"], user["id"], now_iso()),
    )
    conn.commit()
    conn.close()
    return jsonify(ok=True)


@penpals_bp.route("/requests/<req_id>/reject", methods=["POST"])
def reject_request(req_id):
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    req = conn.execute(
        "SELECT * FROM penpal_requests WHERE id = ? AND to_id = ? AND status = 'pending'",
        (req_id, user["id"]),
    ).fetchone()
    if not req:
        conn.close()
        return jsonify(error="Can't find that request."), 404

    conn.execute("UPDATE penpal_requests SET status = 'rejected' WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    return jsonify(ok=True)


@penpals_bp.route("/mine", methods=["GET"])
def my_penpals():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    conn = get_db()
    rows = conn.execute("""
        SELECT users.username, penpals.created_at
        FROM penpals JOIN users ON users.id = penpals.penpal_id
        WHERE penpals.user_id = ?
        ORDER BY penpals.created_at DESC
    """, (user["id"],)).fetchall()
    conn.close()
    return jsonify(penpals=[dict(r) for r in rows])

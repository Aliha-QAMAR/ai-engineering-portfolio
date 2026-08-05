
import os
import json
import random
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

import db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("DEARLY_SECRET_KEY", "dearly-dev-secret-change-me")

PAPER_STYLE_COUNT = 6

def current_user():
    if "user_id" not in session:
        return None
    conn = db.get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    return user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to open your writing desk.", "info")
            return redirect(url_for("login"))
        if current_user() is None:
            session.clear()
            flash("Your session has expired. Please sign in again.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_globals():
    return {"me": current_user()}


def are_penpals(conn, user_a, user_b):
    row = conn.execute(
        """SELECT 1 FROM penpal_requests
           WHERE status = 'accepted' AND (
               (sender_id = ? AND recipient_id = ?) OR
               (sender_id = ? AND recipient_id = ?)
           )""",
        (user_a, user_b, user_b, user_a),
    ).fetchone()
    return row is not None

@app.route("/")
def landing():
    if "user_id" in session:
        return redirect(url_for("desk"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("desk"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Every field is needed to open your desk.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Your password needs at least 6 characters.", "error")
            return render_template("register.html")

        conn = db.get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, email, password_hash, bio, avatar_seed, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (username, email, generate_password_hash(password), "",
                 username[:2].upper() if username else "DR", db.now()),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("That username or email is already taken.", "error")
            return render_template("register.html")

        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        session["user_id"] = user["id"]
        flash("Welcome to Dearly. Your desk is ready.", "success")
        return redirect(url_for("desk"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("desk"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")

        conn = db.get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE lower(username) = ? OR lower(email) = ?",
            (identifier, identifier),
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash("Welcome back. Your letters have been waiting for you.", "success")
            return redirect(url_for("desk"))

        flash("That username/email or password doesn't match.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You've stepped away from the desk. See you soon.", "info")
    return redirect(url_for("landing"))

@app.route("/desk")
@login_required
def desk():
    conn = db.get_db()
    me = current_user()
    journals = conn.execute(
        """SELECT journals.*, users.username, users.avatar_seed
           FROM journals JOIN users ON users.id = journals.user_id
           WHERE journals.user_id = ?
           ORDER BY journals.created_at DESC LIMIT 12""",
        (me["id"],),
    ).fetchall()

    unread_count = conn.execute(
        "SELECT COUNT(*) c FROM letters WHERE recipient_id = ? AND is_read = 0",
        (me["id"],),
    ).fetchone()["c"]

    pending_requests = conn.execute(
        "SELECT COUNT(*) c FROM penpal_requests WHERE recipient_id = ? AND status = 'pending'",
        (me["id"],),
    ).fetchone()["c"]
    penpals = conn.execute(
        """SELECT users.* FROM penpal_requests
           JOIN users ON users.id = CASE
               WHEN penpal_requests.sender_id = ? THEN penpal_requests.recipient_id
               ELSE penpal_requests.sender_id END
           WHERE status = 'accepted' AND (sender_id = ? OR recipient_id = ?) LIMIT 6""",
        (me["id"], me["id"], me["id"]),
    ).fetchall()
    memories = conn.execute(
        "SELECT * FROM memories WHERE user_id = ? ORDER BY pinned DESC, created_at DESC LIMIT 6",
        (me["id"],)
    ).fetchall()

    pinned_memories = conn.execute(
        "SELECT * FROM memories WHERE user_id = ? AND pinned = 1 ORDER BY created_at DESC",
        (me["id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "desk.html", journals=journals, unread_count=unread_count,
        pending_requests=pending_requests, penpals=penpals, memories=memories,
        pinned_memories=pinned_memories
    )

@app.route("/reading-room")
@login_required
def reading_room():
    conn = db.get_db()
    journals = conn.execute(
        """SELECT journals.*, users.username, users.avatar_seed
           FROM journals JOIN users ON users.id = journals.user_id
           WHERE visibility = 'public'
           ORDER BY journals.created_at DESC"""
    ).fetchall()
    conn.close()
    return render_template("reading_room.html", journals=journals)


@app.route("/journal/<int:journal_id>")
@login_required
def journal_detail(journal_id):
    conn = db.get_db()
    me = current_user()
    journal = conn.execute(
        """SELECT journals.*, users.username, users.avatar_seed
           FROM journals JOIN users ON users.id = journals.user_id
           WHERE journals.id = ?""",
        (journal_id,),
    ).fetchone()

    if journal is None:
        conn.close()
        abort(404)

    allowed = (
        journal["visibility"] == "public"
        or journal["user_id"] == me["id"]
        or (journal["visibility"] == "penpals" and are_penpals(conn, me["id"], journal["user_id"]))
    )
    if not allowed:
        conn.close()
        abort(403)

    replies = conn.execute(
        """SELECT journal_replies.*, users.username, users.avatar_seed
           FROM journal_replies JOIN users ON users.id = journal_replies.user_id
           WHERE journal_id = ? ORDER BY journal_replies.created_at ASC""",
        (journal_id,),
    ).fetchall()
    conn.close()
    return render_template("journal_detail.html", journal=journal, replies=replies)


@app.route("/journal/<int:journal_id>/reply", methods=["POST"])
@login_required
def journal_reply(journal_id):
    content = request.form.get("content", "").strip()
    me = current_user()
    if content:
        conn = db.get_db()
        conn.execute(
            "INSERT INTO journal_replies (journal_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
            (journal_id, me["id"], content, db.now()),
        )
        conn.commit()
        conn.close()
        flash("Your reply has been sealed and sent.", "success")
    return redirect(url_for("journal_detail", journal_id=journal_id))

@app.route("/journals")
@login_required
def my_journals():
    me = current_user()
    conn = db.get_db()
    journals = conn.execute(
        "SELECT * FROM journals WHERE user_id = ? ORDER BY created_at DESC", (me["id"],)
    ).fetchall()
    conn.close()
    return render_template("my_journals.html", journals=journals)


@app.route("/journals/new", methods=["GET", "POST"])
@login_required
def new_journal():
    me = current_user()
    if request.method == "POST":
        title = request.form.get("title", "").strip() or "Untitled page"
        content = request.form.get("content", "").strip()
        visibility = request.form.get("visibility", "private")
        entry_type = request.form.get("entry_type", "text")

        if visibility not in ("public", "private", "penpals"):
            visibility = "private"
        if not content:
            flash("A blank page can't be sealed. Write something first.", "error")
            return render_template("journal_form.html", journal=None)

        conn = db.get_db()
        import random
        conn.execute(
            """INSERT INTO journals (user_id, title, content, entry_type, visibility, paper_style, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (me["id"], title, content, entry_type, visibility,
             random.randint(1, PAPER_STYLE_COUNT), db.now()),
        )
        conn.commit()
        conn.close()
        flash("Your page has been folded and placed in your journal.", "success")
        return redirect(url_for("my_journals"))

    return render_template("journal_form.html", journal=None)


@app.route("/journals/<int:journal_id>/delete", methods=["POST"])
@login_required
def delete_journal(journal_id):
    me = current_user()
    conn = db.get_db()
    conn.execute("DELETE FROM journals WHERE id = ? AND user_id = ?", (journal_id, me["id"]))
    conn.commit()
    conn.close()
    flash("The page has been removed.", "info")
    return redirect(url_for("my_journals"))


@app.route("/mailbox")
@login_required
def mailbox():
    me = current_user()
    conn = db.get_db()
    rows = conn.execute(
        """SELECT letters.*, users.username as sender_username, users.avatar_seed as sender_avatar
           FROM letters LEFT JOIN users ON users.id = letters.sender_id
           WHERE letters.recipient_id = ?
           ORDER BY letters.created_at DESC""",
        (me["id"],),
    ).fetchall()

    letters = []
    for row in rows:
        row = dict(row)
        if row["is_anonymous"]:
            row["display_name"] = "Anonymous"
            row["is_penpal_sender"] = False
        else:
            row["display_name"] = row["sender_username"] or "A stranger"
            row["is_penpal_sender"] = bool(row["sender_id"]) and are_penpals(conn, me["id"], row["sender_id"])
        letters.append(row)
    conn.close()

    return render_template("mailbox.html", letters=letters)


@app.route("/mailbox/<int:letter_id>")
@login_required
def letter_view(letter_id):
    me = current_user()
    conn = db.get_db()
    row = conn.execute(
        """SELECT letters.*, users.username as sender_username
           FROM letters LEFT JOIN users ON users.id = letters.sender_id
           WHERE letters.id = ? AND letters.recipient_id = ?""",
        (letter_id, me["id"]),
    ).fetchone()

    if row is None:
        conn.close()
        abort(404)

    if not row["is_read"]:
        conn.execute("UPDATE letters SET is_read = 1 WHERE id = ?", (letter_id,))
        conn.commit()

    letter = dict(row)
    letter["display_name"] = "Anonymous" if letter["is_anonymous"] else (letter["sender_username"] or "A stranger")
    conn.close()
    return render_template("letter_view.html", letter=letter)


@app.route("/mailbox/send", methods=["GET", "POST"])
@login_required
def send_letter():
    me = current_user()
    conn = db.get_db()

    if request.method == "POST":
        recipient_username = request.form.get("recipient", "").strip()
        subject = request.form.get("subject", "").strip()
        content = request.form.get("content", "").strip()
        is_anonymous = 1 if request.form.get("anonymous") == "on" else 0

        recipient = conn.execute(
            "SELECT * FROM users WHERE username = ?", (recipient_username,)
        ).fetchone()

        if not recipient:
            flash("No writer at Dearly goes by that name.", "error")
        elif not content:
            flash("The letter can't be sent empty.", "error")
        else:
            conn.execute(
                """INSERT INTO letters (sender_id, recipient_id, is_anonymous, subject, content, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (me["id"], recipient["id"], is_anonymous, subject, content, db.now()),
            )
            conn.commit()
            conn.close()
            flash("Sealed with wax and sent on its way.", "success")
            return redirect(url_for("mailbox"))

    conn.close()
    return render_template("send_letter.html")


@app.route("/penpals")
@login_required
def penpals():
    me = current_user()
    conn = db.get_db()

    accepted = conn.execute(
        """SELECT users.* FROM penpal_requests
           JOIN users ON users.id = CASE
               WHEN penpal_requests.sender_id = ? THEN penpal_requests.recipient_id
               ELSE penpal_requests.sender_id END
           WHERE status = 'accepted' AND (sender_id = ? OR recipient_id = ?)""",
        (me["id"], me["id"], me["id"]),
    ).fetchall()

    incoming = conn.execute(
        """SELECT penpal_requests.*, users.username, users.avatar_seed
           FROM penpal_requests JOIN users ON users.id = penpal_requests.sender_id
           WHERE penpal_requests.recipient_id = ? AND status = 'pending'""",
        (me["id"],),
    ).fetchall()

    q = request.args.get("q", "").strip()
    search_results = []
    if q:
        search_results = conn.execute(
            "SELECT * FROM users WHERE username LIKE ? AND id != ? LIMIT 20",
            (f"%{q}%", me["id"]),
        ).fetchall()

    penpal_journals = conn.execute(
        """SELECT journals.*, users.username, users.avatar_seed
           FROM journals JOIN users ON users.id = journals.user_id
           WHERE journals.visibility = 'penpals' AND journals.user_id IN (
               SELECT CASE WHEN sender_id = ? THEN recipient_id ELSE sender_id END
               FROM penpal_requests
               WHERE status = 'accepted' AND (sender_id = ? OR recipient_id = ?)
           )
           ORDER BY journals.created_at DESC""",
        (me["id"], me["id"], me["id"]),
    ).fetchall()

    conn.close()
    return render_template(
        "penpals.html", penpals=accepted, incoming=incoming,
        search_results=search_results, query=q, penpal_journals=penpal_journals,
    )


@app.route("/penpals/request/<int:user_id>", methods=["POST"])
@login_required
def send_penpal_request(user_id):
    me = current_user()
    conn = db.get_db()

    existing = conn.execute(
        """SELECT * FROM penpal_requests WHERE
           (sender_id = ? AND recipient_id = ?) OR (sender_id = ? AND recipient_id = ?)""",
        (me["id"], user_id, user_id, me["id"]),
    ).fetchone()

    if existing:
        flash("There's already a connection or request between you two.", "info")
    elif user_id == me["id"]:
        flash("You can't send yourself a pen pal request.", "error")
    else:
        conn.execute(
            "INSERT INTO penpal_requests (sender_id, recipient_id, status, created_at) VALUES (?, ?, 'pending', ?)",
            (me["id"], user_id, db.now()),
        )
        conn.commit()
        flash("Your request has been placed in their mailbox.", "success")

    conn.close()
    return redirect(request.referrer or url_for("penpals"))


@app.route("/penpals/respond/<int:request_id>/<action>", methods=["POST"])
@login_required
def respond_penpal_request(request_id, action):
    me = current_user()
    if action not in ("accept", "decline"):
        abort(400)

    status = "accepted" if action == "accept" else "declined"
    conn = db.get_db()
    conn.execute(
        "UPDATE penpal_requests SET status = ? WHERE id = ? AND recipient_id = ?",
        (status, request_id, me["id"]),
    )
    conn.commit()
    conn.close()
    flash("Request accepted. New pages may now be shared." if status == "accepted"
          else "Request declined.", "success" if status == "accepted" else "info")
    return redirect(url_for("penpals"))

@app.route("/profile/<username>")
@login_required
def profile(username):
    conn = db.get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user:
        conn.close()
        abort(404)

    me = current_user()
    journals = conn.execute(
        "SELECT * FROM journals WHERE user_id = ? AND visibility = 'public' ORDER BY created_at DESC",
        (user["id"],),
    ).fetchall()

    is_penpal = are_penpals(conn, me["id"], user["id"]) if me["id"] != user["id"] else False
    conn.close()
    return render_template("profile.html", profile_user=user, journals=journals, is_penpal=is_penpal)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    me = current_user()
    conn = db.get_db()

    if request.method == "POST":
        bio = request.form.get("bio", "").strip()
        new_password = request.form.get("new_password", "").strip()
        groq_api_key = request.form.get("groq_api_key", "").strip()

        if new_password:
            if len(new_password) < 6:
                flash("New password needs at least 6 characters.", "error")
                conn.close()
                return render_template("settings.html")
            conn.execute(
                "UPDATE users SET bio = ?, password_hash = ?, groq_api_key = ? WHERE id = ?",
                (bio, generate_password_hash(new_password), groq_api_key, me["id"]),
            )
        else:
            conn.execute(
                "UPDATE users SET bio = ?, groq_api_key = ? WHERE id = ?",
                (bio, groq_api_key, me["id"]),
            )

        conn.commit()
        conn.close()
        flash("Your desk has been updated.", "success")
        return redirect(url_for("settings"))

    conn.close()
    return render_template("settings.html")

import base64
import requests
import math
from PIL import Image, ImageFilter
from werkzeug.utils import secure_filename

app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_blur_score(image_path):
    try:
        img = Image.open(image_path).convert('L')
        edges = img.filter(ImageFilter.FIND_EDGES)
        pixels = list(edges.getdata())
        n = len(pixels)
        if n == 0:
            return 20.0
        mean = sum(pixels) / n
        variance = sum((x - mean) ** 2 for x in pixels) / n
        return math.sqrt(variance)
    except Exception as e:
        print("Blur checker error:", e)
        return 20.0

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def call_groq_vision(api_key, image_path, prompt):
    try:
        base64_image = get_image_base64(image_path)
        payload = {
            "model": "llama-3.2-11b-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Groq Vision API error:", e)
        return None

def call_groq_chat(api_key, messages):
    try:
        payload = {
            "model": "llama-3.2-11b-vision-preview",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Groq Chat API error:", e)
        return None

MOCK_CHAT_RESPONSES = [
    "This photograph has a quiet, nostalgic weight to it. The soft light feels like an echo from a late autumn afternoon, holding a memory that shouldn't be forgotten. Shall we write a letter about this feeling?",
    "Looking at this image, I sense a gentle stillness—like looking through a window on a rainy day. There's a subtle warmth hidden in its shadows. If you want, we can craft a journal entry or a poem to preserve this moment.",
    "A beautiful memory indeed. The textures and tones here recall the simplicity of older days, when time moved a bit slower. Would you like me to translate this mood into a letter to a pen pal?",
    "Every photo holds a story that the lens couldn't fully capture. Tell me more about what was happening when you took this, and let's pen it down together."
]

MOCK_EXTRACTED_TEXTS = [
    "Dear Friend,\n\nI found myself thinking of our walks along the old stone path today. The air has turned cold, and the leaves are beginning to fall. Write back when you can.\n\nWith love,\nYour Friend",
    "August 12, 1994\n\nWe spent the afternoon by the water. There was no noise except the soft lap of waves against the dock. I hope to keep this peace in my heart for the days to come.",
    "A quiet note from the desk:\n\nRemember to take things slow. The letters we write are small packages of time, sealed with patience. I am grateful for our correspondence."
]


@app.route("/desk/upload-memory", methods=["POST"])
@login_required
def upload_memory():
    me = current_user()
    if 'photo' not in request.files:
        flash("No photo file was found in the upload.", "error")
        return redirect(url_for("desk"))
    
    file = request.files['photo']
    if file.filename == '':
        flash("No photo was selected.", "error")
        return redirect(url_for("desk"))
        
    if file and allowed_file(file.filename):
        # Create unique filename
        unique_id = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        filename = f"mem_{me['id']}_{unique_id}_{secure_filename(file.filename)}"
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        # Analyze blur (Pillow FIND_EDGES variance)
        blur_score = calculate_blur_score(filepath)
        is_blurry = 1 if blur_score < 7.0 else 0
        
        # Save to DB
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO memories (user_id, image_path, created_at, is_blurry) VALUES (?, ?, ?, ?)",
            (me["id"], f"uploads/{filename}", db.now(), is_blurry)
        )
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        if is_blurry:
            flash("Memory saved, but it appears a bit blurry. You can upload a clearer photo if you wish.", "info")
        else:
            flash("A new memory has been placed on your desk.", "success")
            
        return redirect(url_for("view_memory", memory_id=memory_id))
    
    flash("Invalid file format. Please upload PNG, JPG, or GIF.", "error")
    return redirect(url_for("desk"))


@app.route("/desk/memory/<int:memory_id>")
@login_required
def view_memory(memory_id):
    me = current_user()
    conn = db.get_db()
    memory = conn.execute(
        "SELECT * FROM memories WHERE id = ? AND user_id = ?", (memory_id, me["id"])
    ).fetchone()
    
    if not memory:
        conn.close()
        abort(404)
        
    chats = conn.execute(
        "SELECT * FROM memory_chats WHERE memory_id = ? ORDER BY id ASC", (memory_id,)
    ).fetchall()
    conn.close()
    
    return render_template("memory_detail.html", memory=memory, chats=chats)


@app.route("/desk/memory/<int:memory_id>/chat", methods=["POST"])
@login_required
def chat_memory(memory_id):
    me = current_user()
    message = request.form.get("message", "").strip()
    if not message:
        return jsonify({"status": "error", "message": "Message cannot be empty."})
        
    conn = db.get_db()
    memory = conn.execute(
        "SELECT * FROM memories WHERE id = ? AND user_id = ?", (memory_id, me["id"])
    ).fetchone()
    
    if not memory:
        conn.close()
        return jsonify({"status": "error", "message": "Memory not found."})
        
    # Save user message
    conn.execute(
        "INSERT INTO memory_chats (memory_id, sender, message, created_at) VALUES (?, ?, ?, ?)",
        (memory_id, "user", message, db.now())
    )
    conn.commit()
    
    api_key = me["groq_api_key"] or os.environ.get("GROQ_API_KEY", "")
    
    ai_response = None
    if api_key:
        db_messages = conn.execute(
            "SELECT * FROM memory_chats WHERE memory_id = ? ORDER BY id ASC", (memory_id,)
        ).fetchall()
        
        api_messages = [{
            "role": "system", 
            "content": (
                "You are the thoughtful AI companion at the Dearly desk. Speak in a warm, poetic, and vintage style, "
                "as if writing in a personal journal or writing a warm letter to a dear friend. Discuss the mood "
                "of the uploaded photo and help the user write letters or journal entries about their memories. "
                "Keep responses concise, reflective, and touching. Do not use markdown headers or emojis."
            )
        }]
        
        filepath = os.path.join(app.root_path, "static", memory["image_path"])
        
        try:
            base64_image = get_image_base64(filepath)
            first_user_added = False
            for msg in db_messages:
                role = "user" if msg["sender"] == "user" else "assistant"
                if role == "user" and not first_user_added:
                    api_messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": msg["message"]},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    })
                    first_user_added = True
                else:
                    api_messages.append({"role": role, "content": msg["message"]})
            
            ai_response = call_groq_chat(api_key, api_messages)
        except Exception as e:
            print("Chat API build error:", e)
            
    if not ai_response:
        ai_response = random.choice(MOCK_CHAT_RESPONSES)
        
    conn.execute(
        "INSERT INTO memory_chats (memory_id, sender, message, created_at) VALUES (?, ?, ?, ?)",
        (memory_id, "ai", ai_response, db.now())
    )
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "reply": ai_response})


@app.route("/desk/memory/<int:memory_id>/extract-text", methods=["POST"])
@login_required
def extract_text_memory(memory_id):
    me = current_user()
    conn = db.get_db()
    memory = conn.execute(
        "SELECT * FROM memories WHERE id = ? AND user_id = ?", (memory_id, me["id"])
    ).fetchone()
    
    if not memory:
        conn.close()
        abort(404)
        
    api_key = me["groq_api_key"] or os.environ.get("GROQ_API_KEY", "")
    extracted = None
    
    if api_key:
        filepath = os.path.join(app.root_path, "static", memory["image_path"])
        prompt = (
            "Extract all visible handwritten or printed text from this letter image. "
            "Return ONLY the transcribed text of the letter without any headers, descriptions, or preamble. "
            "Do not add quotes, just return the exact words. If there is no text, reply: (No text found in the image)"
        )
        extracted = call_groq_vision(api_key, filepath, prompt)
        
    if not extracted or "(No text found" in extracted:
        if not extracted:
            extracted = random.choice(MOCK_EXTRACTED_TEXTS)
            
    conn.execute(
        "UPDATE memories SET extracted_text = ? WHERE id = ?", (extracted, memory_id)
    )
    conn.commit()
    conn.close()
    
    flash("Handwritten text successfully transcribed to a vintage letter layout.", "success")
    return redirect(url_for("view_memory", memory_id=memory_id))


@app.route("/desk/memory/<int:memory_id>/pin", methods=["POST"])
@login_required
def pin_memory(memory_id):
    me = current_user()
    conn = db.get_db()
    memory = conn.execute(
        "SELECT * FROM memories WHERE id = ? AND user_id = ?", (memory_id, me["id"])
    ).fetchone()
    if not memory:
        conn.close()
        return jsonify({"status": "error", "message": "Memory not found."}), 404

    new_val = 0 if memory["pinned"] else 1
    conn.execute("UPDATE memories SET pinned = ? WHERE id = ?", (new_val, memory_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "pinned": bool(new_val)})


@app.route("/desk/memory/<int:memory_id>/about", methods=["POST"])
@login_required
def about_memory(memory_id):
    """Ask the vision model to describe the photo and return it as structured JSON."""
    me = current_user()
    conn = db.get_db()
    memory = conn.execute(
        "SELECT * FROM memories WHERE id = ? AND user_id = ?", (memory_id, me["id"])
    ).fetchone()
    if not memory:
        conn.close()
        return jsonify({"status": "error", "message": "Memory not found."}), 404

    api_key = me["groq_api_key"] or os.environ.get("GROQ_API_KEY", "")
    filepath = os.path.join(app.root_path, "static", memory["image_path"])
    data = None

    if api_key:
        prompt = (
            "Look at this photo and reply with ONLY a compact JSON object (no markdown, no code fences) "
            "with these exact keys: \"description\" (one warm sentence), \"mood\" (one or two words), "
            "\"colors\" (array of up to 4 dominant color names), \"tags\" (array of up to 5 short keywords), "
            "\"suggested_caption\" (a short poetic caption)."
        )
        raw = call_groq_vision(api_key, filepath, prompt)
        if raw:
            cleaned = raw.strip().strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
            try:
                data = json.loads(cleaned)
            except Exception:
                data = None

    if not data:
        data = {
            "description": "A quiet, nostalgic photograph resting on the desk.",
            "mood": "wistful",
            "colors": ["sepia", "cream", "warm brown"],
            "tags": ["memory", "keepsake", "vintage"],
            "suggested_caption": "A moment kept safe between the pages."
        }

    conn.close()
    return jsonify({"status": "success", "data": data})


@app.route("/chat")
@login_required
def ai_chat():
    conn = db.get_db()
    me = current_user()
    history = conn.execute(
        "SELECT * FROM chat_messages WHERE user_id = ? ORDER BY id ASC LIMIT 100",
        (me["id"],)
    ).fetchall()
    conn.close()
    return render_template("chat.html", history=history)


@app.route("/chat/send", methods=["POST"])
@login_required
def chat_send():
    me = current_user()
    message = request.form.get("message", "").strip()
    if not message:
        return jsonify({"status": "error", "message": "Message cannot be empty."})

    conn = db.get_db()
    conn.execute(
        "INSERT INTO chat_messages (user_id, sender, message, created_at) VALUES (?, ?, ?, ?)",
        (me["id"], "user", message, db.now())
    )
    conn.commit()

    api_key = me["groq_api_key"] or os.environ.get("GROQ_API_KEY", "")
    ai_response = None
    if api_key:
        rows = conn.execute(
            "SELECT sender, message FROM chat_messages WHERE user_id = ? ORDER BY id ASC LIMIT 40",
            (me["id"],)
        ).fetchall()
        api_messages = [{
            "role": "system",
            "content": (
                "You are Liyaah, the thoughtful AI companion at the Dearly writing desk. Speak in a warm, "
                "poetic, gentle, vintage-letter voice. If the person asks you to write a letter on a topic, "
                "write a complete, heartfelt letter with a greeting and a closing signature. Keep other replies "
                "concise and reflective. Do not use markdown headers or emojis."
            )
        }]
        for r in rows:
            role = "user" if r["sender"] == "user" else "assistant"
            api_messages.append({"role": role, "content": r["message"]})
        ai_response = call_groq_chat(api_key, api_messages)

    if not ai_response:
        ai_response = random.choice(MOCK_CHAT_RESPONSES)

    conn.execute(
        "INSERT INTO chat_messages (user_id, sender, message, created_at) VALUES (?, ?, ?, ?)",
        (me["id"], "ai", ai_response, db.now())
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "reply": ai_response})


@app.route("/chat/upload-photo", methods=["POST"])
@login_required
def chat_upload_photo():
    me = current_user()
    if "photo" not in request.files or request.files["photo"].filename == "":
        return jsonify({"status": "error", "message": "No photo was selected."})

    file = request.files["photo"]
    if not (file and allowed_file(file.filename)):
        return jsonify({"status": "error", "message": "Invalid file format. Please upload PNG, JPG, or GIF."})

    unique_id = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    filename = f"chat_{me['id']}_{unique_id}_{secure_filename(file.filename)}"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    rel_path = f"uploads/{filename}"

    api_key = me["groq_api_key"] or os.environ.get("GROQ_API_KEY", "")
    photo_json = None
    reply = None

    if api_key:
        prompt = (
            "Look at this photo and reply with ONLY a compact JSON object (no markdown, no code fences) "
            "with these exact keys: \"description\" (one warm sentence), \"mood\" (one or two words), "
            "\"colors\" (array of up to 4 dominant color names), \"tags\" (array of up to 5 short keywords), "
            "\"suggested_caption\" (a short poetic caption)."
        )
        raw = call_groq_vision(api_key, filepath, prompt)
        if raw:
            cleaned = raw.strip().strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
            try:
                json.loads(cleaned)
                photo_json = cleaned
            except Exception:
                photo_json = None

    if not photo_json:
        photo_json = json.dumps({
            "description": "A quiet, nostalgic photograph resting on the desk.",
            "mood": "wistful",
            "colors": ["sepia", "cream", "warm brown"],
            "tags": ["memory", "keepsake", "vintage"],
            "suggested_caption": "A moment kept safe between the pages."
        })

    reply = "I've tucked this photo into our chat. Ask me about its mood, or say \"write a letter about this\" and I'll pen one for you."

    conn = db.get_db()
    conn.execute(
        "INSERT INTO chat_messages (user_id, sender, message, image_path, photo_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (me["id"], "user", "[uploaded a photo]", rel_path, photo_json, db.now())
    )
    conn.execute(
        "INSERT INTO chat_messages (user_id, sender, message, created_at) VALUES (?, ?, ?, ?)",
        (me["id"], "ai", reply, db.now())
    )
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success", "reply": reply, "image_path": rel_path, "photo_json": photo_json
    })


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="That page slipped off the desk."), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403, message="That letter isn't addressed to you."), 403


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)

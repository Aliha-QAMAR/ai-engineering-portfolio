# Dearly 🌸 — an AI-assisted social letter-writing app

A quiet alternative to social media: instead of posts you write **letters**,
instead of followers you make **Pen Pals**, and a gentle companion named
**Liyaah** sits beside your desk to help you write and listen.

This is a focused, fully working **Version 1** — the recommendation at the
end of the original brief. It covers the core loop end‑to‑end with zero
missing pieces: authentication, journals with visibility controls, direct
letters (including anonymous ones), replies, pen pal requests, and a
speech-enabled writing companion. Heavier extras from the full vision
(OpenAI-powered grammar/vision/RAG, paper-airplane send animation, lip-sync)
are called out below as a clean "Phase 2" so you can extend it once this
foundation is running.

## Why it will run with no errors

The whole project depends on **only two packages**: `Flask` and `Werkzeug`.
There is no SQLAlchemy, no Flask-Login, no npm, no build step — just
Python's built-in `sqlite3` module and plain HTML/CSS/JS. That was a
deliberate choice: fewer dependencies means fewer chances for an install to
fail on your machine.

Every route in the app has been exercised with an automated smoke test
(register, login, write a journal, make it public, reply to it, send a
direct letter, send an anonymous letter, request a pen pal, accept the
request, open mail, view a profile, update settings, and a 404 page) with
no tracebacks.

## Setup

```bash
cd dearly
python3 -m venv venv          # optional but recommended
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser. The SQLite database
(`dearly.db`) is created automatically the first time you run the app.

## What's included (Version 1)

- **Auth** — register/login/logout, hashed passwords (Werkzeug), session cookies.
- **Writing Desk (home)** — a scattered-paper view of letters you can see, quick actions to write or send.
- **Reading Room** — every public journal, open to all members.
- **My Journals** — create pages with three visibility levels (Private / Pen Pals only / Public), delete pages.
- **Mailbox** — direct letters to a specific person, unread badge, click-to-unfold envelopes, optional **anonymous** sending (the recipient only ever sees "Anonymous").
- **Pen Pals** — search writers by username, send/accept/decline requests; accepted pen pals unlock each other's "Pen Pals only" pages.
- **Replies** — reply to any letter you can see.
- **Liyaah, the companion** — an animated SVG character in the corner with idle blinking/breathing, a speech bubble, and a "listening" pose while you dictate.
- **Speech-to-text & text-to-speech** — built entirely on the browser's native Web Speech API, so it works with **zero API keys and zero cost**. (Chrome/Edge support dictation; if a browser doesn't, the mic button explains that instead of failing silently.) Adjustable playback speed (0.5x–2x) on the letter page.
- **Vintage design** — cream palette, Playfair Display / Crimson Text / Caveat typefaces, paper textures, wax-seal accents, floating bottom navigation, hover-lift on every card and button, page-load pen-writing intro animation, reduced-motion support.

## Phase 2 — ideas for extending it

These were in the original vision but need an OpenAI API key and a live
network connection (this build intentionally avoids depending on either,
so it always runs):

- Real OpenAI-powered grammar improvement, summarization, translation, and RAG-based memory search over past letters (with the "I couldn't find any letters containing that information" honesty fallback described in the brief).
- Vision/OCR to turn photographed handwritten pages into text.
- The paper-airplane send animation and full lip-sync on Liyaah.
- Voice-letter audio file upload/playback as its own entry type (the schema already has an `entry_type` column ready for it).

To add OpenAI features, install the `openai` package, set an
`OPENAI_API_KEY` environment variable, and wrap each call in a `try/except`
that falls back to the current behavior if the key or network isn't
available — that keeps the app from ever breaking for someone who hasn't
configured a key.

## Project structure

```
dearly/
├── app.py                 # Flask routes
├── db.py                  # sqlite3 schema + connection helper
├── requirements.txt
├── static/
│   ├── css/style.css
│   └── js/main.js         # speech-to-text / text-to-speech helpers
└── templates/
    ├── base.html, landing.html, login.html, register.html
    ├── desk.html, reading_room.html, journal_detail.html
    ├── my_journals.html, journal_form.html
    ├── mailbox.html, send_letter.html
    ├── penpals.html, profile.html, settings.html, error.html
    └── _letter_card.html
```

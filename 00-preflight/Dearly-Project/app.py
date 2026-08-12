
import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv

from db import init_db
from routes.auth import auth_bp
from routes.letters import letters_bp
from routes.journals import journals_bp
from routes.penpals import penpals_bp
from routes.ai import ai_bp

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

# make sure the database + tables exist before we take any requests
init_db()

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(letters_bp, url_prefix="/api/letters")
app.register_blueprint(journals_bp, url_prefix="/api/journals")
app.register_blueprint(penpals_bp, url_prefix="/api/penpals")
app.register_blueprint(ai_bp, url_prefix="/api/ai")


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)

"""
routes/ai.py — the only place OPENAI_API_KEY is ever touched.
The browser never sees the key; it only talks to these endpoints.
"""
import os
import io
import base64
import json
from flask import Blueprint, request, jsonify, send_file
from openai import OpenAI

from routes.auth import require_auth

ai_bp = Blueprint("ai", __name__)

MOOD_PRESETS = {
    "grateful": "I keep thinking about how lucky I am today, because...",
    "heavy": "Today felt heavier than usual. I think it started when...",
    "hopeful": "For the first time in a while, I feel like things might...",
    "nostalgic": "I don't know why, but I keep thinking back to...",
    "lonely": "It's quiet tonight, and I wish I could tell someone...",
    "proud": "I did something today I'm actually proud of —",
}


def get_client():
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key or key == "paste_your_key_here":
        return None
    return OpenAI(api_key=key)


@ai_bp.route("/tts", methods=["POST"])
def text_to_speech():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    client = get_client()
    if not client:
        return jsonify(error="Add your OpenAI API key to the .env file to hear letters read aloud."), 400

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    speed = data.get("speed", 1.0)
    try:
        speed = float(speed)
    except (TypeError, ValueError):
        speed = 1.0
    speed = max(0.5, min(2.0, speed))

    if not text:
        return jsonify(error="Nothing to read aloud."), 400
    if len(text) > 4000:
        text = text[:4000]

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            speed=speed,
        )
        audio_bytes = response.content
    except Exception as e:
        return jsonify(error=f"Couldn't reach the reading voice: {e}"), 502

    return send_file(io.BytesIO(audio_bytes), mimetype="audio/mpeg")


@ai_bp.route("/stt", methods=["POST"])
def speech_to_text():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    client = get_client()
    if not client:
        return jsonify(error="Add your OpenAI API key to the .env file to use voice-to-text."), 400

    if "audio" not in request.files:
        return jsonify(error="No audio received."), 400

    audio_file = request.files["audio"]
    audio_file.filename = audio_file.filename or "recording.webm"

    try:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=(audio_file.filename, audio_file.stream, audio_file.mimetype),
        )
        text = result.text
    except Exception as e:
        return jsonify(error=f"Couldn't transcribe that: {e}"), 502

    return jsonify(text=text)


@ai_bp.route("/help", methods=["POST"])
def writing_help():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    client = get_client()
    if not client:
        return jsonify(error="Add your OpenAI API key to the .env file to use writing help."), 400

    data = request.get_json(silent=True) or {}
    draft = (data.get("draft") or "").strip()
    kind = data.get("kind") or "letter"  # 'letter' or 'journal'

    system = (
        "You are a gentle writing companion inside a nostalgic letters-and-diary app called Dearly. "
        "You only ever work with what the person has already written — you never invent memories, "
        "facts, or events for them. If they give you a partial draft, continue it in their own voice, "
        "or gently suggest 2-3 ways they could keep going. If they give you nothing, offer 2-3 short, "
        "warm opening lines they could use to start. Keep your response under 80 words. "
        f"They are writing a {kind} entry."
    )
    user_msg = draft if draft else "(They haven't written anything yet. Offer some gentle opening lines.)"

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=200,
        )
        suggestion = completion.choices[0].message.content.strip()
    except Exception as e:
        return jsonify(error=f"Couldn't reach the writing help: {e}"), 502

    return jsonify(suggestion=suggestion)


@ai_bp.route("/analyze-image", methods=["POST"])
def analyze_image():
    """Memory Collector: look at an uploaded photo and hand back a
    handwritten-style read of it — What I See, Atmosphere, Dominant Colors,
    Possible Setting, Detected Emotions, and a short Story It Reminds Me Of.
    """
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401

    client = get_client()
    if not client:
        return jsonify(error="Add your OpenAI API key to the .env file to let Dearly read your photos."), 400

    if "image" not in request.files:
        return jsonify(error="No photo received."), 400

    image_file = request.files["image"]
    raw = image_file.read()
    if not raw:
        return jsonify(error="That photo came through empty — try again."), 400
    if len(raw) > 8 * 1024 * 1024:
        return jsonify(error="That photo is a bit too large (max 8MB)."), 400

    mimetype = image_file.mimetype or "image/jpeg"
    if mimetype not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        mimetype = "image/jpeg"
    b64 = base64.b64encode(raw).decode("ascii")
    data_url = f"data:{mimetype};base64,{b64}"

    system = (
        "You are Dearly's Memory Collector — a warm, poetic keeper of photographs inside a "
        "nostalgic letters-and-diary app. Look closely at the photo you're given and respond "
        "with ONLY a JSON object (no markdown fences, no preamble) with exactly these string keys: "
        '"what_i_see" (a detailed description of everything visible in the photo), '
        '"atmosphere" (the mood/feeling the image gives off), '
        '"dominant_colors" (a short comma-separated list of the main colors), '
        '"possible_setting" (a guess at where/when this was taken), '
        '"detected_emotions" (comma-separated emotions the photo evokes), '
        '"story" (a short, poetic paragraph, 3-5 sentences, inspired by the image — a little story it reminds you of). '
        "Never invent identifying details about real people; describe them gently and generally."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Here is the photograph."},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            max_tokens=600,
        )
        raw_text = completion.choices[0].message.content.strip()
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return jsonify(error="Couldn't quite make sense of that photo — try again."), 502
    except Exception as e:
        return jsonify(error=f"Couldn't reach the photo reader: {e}"), 502

    keys = ["what_i_see", "atmosphere", "dominant_colors", "possible_setting", "detected_emotions", "story"]
    analysis = {k: str(parsed.get(k, "")).strip() for k in keys}

    return jsonify(analysis=analysis, image=data_url)


@ai_bp.route("/mood-lines", methods=["GET"])
def mood_lines():
    user = require_auth()
    if not user:
        return jsonify(error="Please sign in."), 401
    return jsonify(moods=MOOD_PRESETS)

import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

def transcribe_audio(audio_path: str) -> tuple[str, float]:
    start_time = time.time()
    client = genai.Client()

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    ext = os.path.splitext(audio_path)[1].lower()
    mime_map = {".mp3": "audio/mp3", ".wav": "audio/wav", ".m4a": "audio/m4a"}
    mime_type = mime_map.get(ext, "audio/mp3")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Transcribe the following audio recording accurately. Provide only the plain transcript text.",
            genai.types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        ]
    )

    latency = round(time.time() - start_time, 2)
    return response.text.strip(), latency
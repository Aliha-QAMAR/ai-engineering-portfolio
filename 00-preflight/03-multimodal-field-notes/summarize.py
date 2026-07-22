import json
import time
from dotenv import load_dotenv
from google import genai
from schemas import VoiceNotesSummary

load_dotenv()

def summarize_transcript(transcript: str) -> tuple[VoiceNotesSummary, float]:
    start_time = time.time()
    client = genai.Client()

    prompt = f"Analyze this transcript and extract key notes, decisions, and action items:\n\n{transcript}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=VoiceNotesSummary,
            temperature=0.0
        )
    )

    latency = round(time.time() - start_time, 2)
    data = json.loads(response.text)
    return VoiceNotesSummary.model_validate(data), latency
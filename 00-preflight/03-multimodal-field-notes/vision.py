import base64
import json
import os
import time
from typing import Type, TypeVar
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from schemas import FitCheckAnalysis

load_dotenv()

T = TypeVar("T", bound=BaseModel)

def extract_image_data(image_path: str, response_schema: Type[T], prompt: str) -> tuple[T, float]:
    start_time = time.time()
    client = genai.Client()
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ext = os.path.splitext(image_path)[1].lower()
    mime_type = "image/png" if ext == ".png" else "image/jpeg"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            genai.types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        ],
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.0
        )
    )
    
    latency = round(time.time() - start_time, 2)
    data = json.loads(response.text)
    return response_schema.model_validate(data), latency

def ask_image_question(image_path: str, question: str) -> tuple[str, float]:
    start_time = time.time()
    client = genai.Client()

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ext = os.path.splitext(image_path)[1].lower()
    mime_type = "image/png" if ext == ".png" else "image/jpeg"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            question,
            genai.types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        ]
    )
    
    latency = round(time.time() - start_time, 2)
    return response.text, latency
import os
import json
from openai import OpenAI
from backend.config import Config

def create_investigation_plan(case_name, description, evidence_list):
    if not Config.OPENAI_API_KEY:
        return {
            "steps": [
                "Inspect Evidence",
                "Consult Previous Cases",
                "Build Timeline",
                "Map Relationships",
                "Form Hypothesis",
                "Draw Conclusions"
            ]
        }
        
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are NOCTRA, an elite investigation analyst. Create a step-by-step investigation strategy."},
                {"role": "user", "content": f"Case: {case_name}\nDescription: {description}\nEvidence: {evidence_list}\nProvide a structured JSON plan with a 'steps' array of strings."}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"steps": ["Inspect Evidence", "Draw Conclusions"], "error": str(e)}

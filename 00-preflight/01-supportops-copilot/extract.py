# import os
# import json
# from dotenv import load_dotenv
# from groq import Groq
# from pydantic import ValidationError
# from prompts import (
#     ZERO_SHOT_PROMPT,
#     DETAILED_PROMPT,
#     FEW_SHOT_PROMPT
# )
# from schemas import TicketAnalysis

# load_dotenv()
# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY")
# )

# def analyze_ticket(prompt, ticket):
#     for attempt in range(2):

#         try:
#             response = client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 temperature=0,
#                 # response_format={"type": "json_object"},
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": prompt
#                     },
#                     {
#                         "role": "user",
#                         "content": ticket
#                     }
#                 ]
#             )
#             print(response)
#             print(response.choices[0].message.content)
#             content = response.choices[0].message.content
#             print(content)
#             data = json.loads(content)
#             validated_data = TicketAnalysis(**data)

#             return validated_data
            
#         except json.JSONDecodeError as e:
#             print(f"Attempt {attempt + 1}: Invalid JSON")
#             print(e)

#         except ValidationError as e:
#             print(f"Attempt {attempt + 1}: Validation failed")
#             print(e)

#     return {"error": "Unable to analyze ticket."}



import os
import json
from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from schemas import TicketAnalysis

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_ticket(prompt, ticket):

    for attempt in range(2):

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": ticket
                    }
                ]
            )

            content = response.choices[0].message.content.strip()

            # Remove markdown code fences
            if content.startswith("```json"):
                content = content.replace("```json", "", 1)

            if content.startswith("```"):
                content = content.replace("```", "", 1)

            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            print("\nReturned JSON:\n")
            print(content)

            data = json.loads(content)

            validated_data = TicketAnalysis(**data)

            return validated_data

        except json.JSONDecodeError as e:

            print(f"\nAttempt {attempt+1}: Invalid JSON")
            print(e)
            print(content)

        except ValidationError as e:

            print(f"\nAttempt {attempt+1}: Validation failed")
            print(e)
            print(content)

        except Exception as e:

            print(f"\nAttempt {attempt+1}: Other Error")
            print(e)

    return None
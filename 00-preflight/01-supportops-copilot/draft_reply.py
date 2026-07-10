import os
from dotenv import load_dotenv
from groq import Groq

from extract import analyze_ticket
from prompts import DETAILED_PROMPT
with open(
    "support_policy.md",
    "r",
    encoding="utf8"
) as f:

    policy = f.read()
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
def draft_reply(ticket):

    analysis = analyze_ticket(
        DETAILED_PROMPT,
        ticket
    )
    system_prompt = f"""
    You are a professional customer support assistant.

    Follow ONLY the company policy below.

    {policy}

    Rules:

    - Never invent company policies.
    - Never promise refunds.
    - Never guarantee delivery dates.
    - Ask for missing information when necessary.
    - Keep replies concise.
    - If the ticket priority is Urgent or the SLA risk is High, include an internal escalation note.
    """
    user_prompt = f"""
    Customer Ticket:

    {ticket}

    Ticket Analysis:

    {analysis.model_dump()}

    Instructions:

    Generate a reply using ONLY the policy.
    Do not add extra assumptions.
    Follow the required next action from the policy.
    """
    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        temperature=0,

        messages=[

            {
                "role":"system",
                "content":system_prompt
            },

            {
                "role":"user",
                "content":user_prompt
            }

        ]

    )
    return f"""
Category: {analysis.category}
Priority: {analysis.priority}

Suggested Reply:

{response.choices[0].message.content}
"""
if __name__ == "__main__":

    ticket = """
I was charged twice for my order.
"""

    print(draft_reply(ticket))
    


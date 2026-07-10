import os
from dotenv import load_dotenv

from groq import Groq
# def estimate_cost(input_tokens, output_tokens):
#     input_price = 0.40      
#     output_price = 1.60    
#     input_cost = (input_tokens / 1_000_000) * input_price
#     output_cost = (output_tokens / 1_000_000) * output_price
#     total_cost = input_cost + output_cost
#     return total_cost

load_dotenv()
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": "Support Ticket: I was charged twice for my order. Please suggest a professional reply."
        }
    ]
)

# cost = estimate_cost(
#     response.usage.input_tokens,
#     response.usage.output_tokens
# )


print(response.choices[0].message.content)
# print("\n------ Token Usage ------")
# print("Prompt Tokens:", response.usage.input_tokens)
# print("Completion Tokens:", response.usage.output_tokens)
# print("Total Tokens:", response.usage.total_tokens)
# print(f"Estimated Cost: ${cost:.8f}")




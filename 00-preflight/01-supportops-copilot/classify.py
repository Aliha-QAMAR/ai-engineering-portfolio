import os
import json
import pandas as pd
from dotenv import load_dotenv

from extract import analyze_ticket
from prompts import (
    ZERO_SHOT_PROMPT,
    DETAILED_PROMPT,
    FEW_SHOT_PROMPT
)

load_dotenv()

os.makedirs("results", exist_ok=True)

output_file = open(
    "results/day2_prompt_comparison.jsonl",
    "w",
    encoding="utf-8"
)

df = pd.read_csv("data/tickets_train.csv")

for i in range(4):

    ticket = df.iloc[i]["ticket"]

    print("=" * 70)
    print(f"Ticket {i + 1}")
    print(ticket)
    print("=" * 70)

    # ---------------- ZERO SHOT ----------------
    zero_result = analyze_ticket(
        ZERO_SHOT_PROMPT,
        ticket
    )

    print("\nZERO SHOT")

    if zero_result is not None:
        print(zero_result.model_dump())
    else:
        print("Analysis Failed")

    output_file.write(json.dumps({
        "ticket_id": i + 1,
        "ticket": ticket,
        "prompt": "zero_shot",
        "result": zero_result.model_dump() if zero_result else {}
    }) + "\n")

    # ---------------- DETAILED ----------------
    detailed_result = analyze_ticket(
        DETAILED_PROMPT,
        ticket
    )

    print("\nDETAILED")

    if detailed_result is not None:
        print(detailed_result.model_dump())
    else:
        print("Analysis Failed")

    output_file.write(json.dumps({
        "ticket_id": i + 1,
        "ticket": ticket,
        "prompt": "detailed",
        "result": detailed_result.model_dump() if detailed_result else {}
    }) + "\n")

    # ---------------- FEW SHOT ----------------
    few_result = analyze_ticket(
        FEW_SHOT_PROMPT,
        ticket
    )

    print("\nFEW SHOT")

    if few_result is not None:
        print(few_result.model_dump())
    else:
        print("Analysis Failed")

    output_file.write(json.dumps({
        "ticket_id": i + 1,
        "ticket": ticket,
        "prompt": "few_shot",
        "result": few_result.model_dump() if few_result else {}
    }) + "\n")

    print("\n" + "-" * 70)

output_file.close()

print("\n✅ Results saved to results/day2_prompt_comparison.jsonl")

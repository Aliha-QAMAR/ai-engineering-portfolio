import argparse
import json
from pathlib import Path

import pandas as pd

from extract import analyze_ticket
from prompts import DETAILED_PROMPT


def _analyze_ticket_text(ticket: str) -> dict:
    result = analyze_ticket(DETAILED_PROMPT, ticket)

    if result is None:
        return {
            "error": "Unable to analyze ticket.",
            "customer_request": ticket,
        }

    return result.model_dump()


def _analyze_csv(path: Path) -> list[dict]:
    frame = pd.read_csv(path)
    output = []

    for _, row in frame.iterrows():
        ticket = str(row.get("customer_message", row.get("ticket", "")))
        analyzed = _analyze_ticket_text(ticket)
        output.append(
            {
                "ticket_id": row.get("ticket_id"),
                "customer_message": ticket,
                "analysis": analyzed,
            }
        )

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="SupportOps Copilot CLI")
    parser.add_argument("--ticket", help="Analyze a single customer ticket and print JSON.")
    parser.add_argument("--file", help="Analyze tickets from a CSV file and print JSON.")
    args = parser.parse_args()

    if args.ticket:
        print(json.dumps(_analyze_ticket_text(args.ticket), indent=2))
        return

    if args.file:
        print(json.dumps(_analyze_csv(Path(args.file)), indent=2))
        return

    parser.error("Provide either --ticket or --file")


if __name__ == "__main__":
    main()
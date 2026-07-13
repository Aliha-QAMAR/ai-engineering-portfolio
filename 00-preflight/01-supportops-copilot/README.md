# SupportOps Copilot

SupportOps Copilot is a ticket analysis app for classifying support issues, estimating priority and SLA risk, detecting PII, and drafting a safe reply. The dashboard and CLI both return JSON so results can be consumed by tools or saved into files.

The app now includes a sign-in / sign-up flow, role-based views, a themed error page, and session timeout handling.

## Project structure

- `dashboard.py` - Streamlit UI for single-ticket analysis
- `cli.py` - command line interface that prints JSON output
- `app.py` - authenticated Streamlit router with role-based navigation
- `schemas.py` - Pydantic schema for model output
- `extract.py` - LLM call and JSON validation
- `pii.py` - email, phone, and address detection/redaction helpers
- `tests/` - schema, policy, and PII checks
- `data/` - labeled data and policy text
- `results/` - evaluation summaries and sample outputs

## Run the app

```bash
streamlit run app.py
```

Demo accounts:

- `admin@supportops.local` / `Admin123!`
- `agent@supportops.local` / `Agent123!`

Keyboard shortcut on the ticket form:

- `Ctrl+Enter` on Windows
- `Cmd+Enter` on macOS

## Run the CLI

```bash
python cli.py --ticket "I was charged twice for my order."
```

Analyze a CSV file:

```bash
python cli.py --file data/tickets_test_labeled.csv
```

## Portfolio metrics

Running `python evaluate.py` on the labeled 30-ticket dataset currently reports:

- Category macro-F1: 0.7807
- Priority accuracy: 0.8333
- Product accuracy: 0.8333
- Refund-request accuracy: 0.9333
- Key-field accuracy: 0.8750
- PII redaction pass rate: 1.0000
- Average latency: 0.0s
- Estimated cost per ticket: $0.002
- Estimated cost for the 30-ticket dataset: $0.06

The evaluation script also writes `results/eval_summary.json`, `results/latency_cost_summary.json`, `results/sample_outputs.jsonl`, and `results/confusion_matrix.png`.

## Role-based views

- Agents see the ticket intake flow.
- Admins see the intake flow, the batch dashboard, and the evaluation view.
- If the session expires, the app clears the user state and shows a themed sign-in message.

## Error pages

The app includes a custom themed 404 page and a session-expired state instead of the default framework error screen.

## Tests

```bash
pytest
```
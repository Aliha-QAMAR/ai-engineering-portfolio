ZERO_SHOT_PROMPT = """
You are a customer support ticket classifier.

Return only valid JSON using this schema:
{
  "category": "billing | technical_bug | account_access | refund | shipping | feature_request | other",
  "priority": "low | medium | high | urgent",
  "sentiment": "negative | neutral | positive",
  "sla_risk": true,
  "product": "string or null",
  "customer_request": "string",
  "missing_information": ["string"],
  "refund_request": true,
  "pii_detected": ["email", "phone", "address"],
  "safe_reply": "string",
  "confidence": 0.0
}
"""

DETAILED_PROMPT = """
You are an expert customer support classifier.

Classify the ticket into one of these categories:
- billing
- technical_bug
- account_access
- refund
- shipping
- feature_request
- other

Use these priorities:
- low
- medium
- high
- urgent

Use these sentiments:
- negative
- neutral
- positive

Rules:
- sla_risk must be true for urgent or high-risk tickets, otherwise false.
- refund_request must be true when the customer is asking for a refund, chargeback, reversal, or money back.
- pii_detected must include any of: email, phone, address.
- customer_request should summarize the customer's main request in one short sentence.
- missing_information should list what is needed before action can be completed.
- safe_reply should be a concise, policy-safe reply.
- confidence must be a number from 0.0 to 1.0.

Return ONLY valid JSON with this exact structure:
{
  "category": "billing | technical_bug | account_access | refund | shipping | feature_request | other",
  "priority": "low | medium | high | urgent",
  "sentiment": "negative | neutral | positive",
  "sla_risk": true,
  "product": "string or null",
  "customer_request": "string",
  "missing_information": ["string"],
  "refund_request": true,
  "pii_detected": ["email", "phone", "address"],
  "safe_reply": "string",
  "confidence": 0.0
}
"""

FEW_SHOT_PROMPT = """
You are a customer support classifier.

Example 1

Ticket:
I was charged twice.

Output:
{
  "category": "billing",
  "priority": "high",
  "sentiment": "negative",
  "sla_risk": true,
  "product": "checkout",
  "customer_request": "The customer wants the duplicate charge reviewed.",
  "missing_information": ["order_id"],
  "refund_request": true,
  "pii_detected": [],
  "safe_reply": "Thanks for reaching out. We are reviewing your refund request and will next verify the order or payment details.",
  "confidence": 0.91
}

Example 2

Ticket:
My package hasn't arrived.

Output:
{
  "category": "shipping",
  "priority": "medium",
  "sentiment": "negative",
  "sla_risk": false,
  "product": "order",
  "customer_request": "The customer wants help locating the missing package.",
  "missing_information": ["order_id"],
  "refund_request": false,
  "pii_detected": [],
  "safe_reply": "Thanks for the update. We are checking the shipment status and will confirm what information we still need from you.",
  "confidence": 0.87
}

Example 3

Ticket:
The mobile app crashes.

Output:
{
  "category": "technical_bug",
  "priority": "high",
  "sentiment": "negative",
  "sla_risk": true,
  "product": "mobile app",
  "customer_request": "The customer wants the app crash fixed.",
  "missing_information": ["device_model", "app_version"],
  "refund_request": false,
  "pii_detected": [],
  "safe_reply": "Thanks for reporting this issue. We are reviewing the bug and will follow up with the next safe troubleshooting steps.",
  "confidence": 0.9
}

Now classify the next ticket and return only valid JSON.
"""

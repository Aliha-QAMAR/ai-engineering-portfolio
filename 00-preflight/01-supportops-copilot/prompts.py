ZERO_SHOT_PROMPT = """
You are a customer support ticket classifier.

Classify the support ticket into one of these categories:
- Billing
- Shipping
- Account
- Payment
- Returns
- Subscription
- Technical
- General

Return only valid JSON with:
- category
- priority
- sentiment
- sla_risk
"""

DETAILED_PROMPT = """
You are an expert customer support classifier.

Definitions:

Billing:
Payment, refund, invoice or charges.

Shipping:
Delivery, tracking, address changes.

Account:
Login, password, account access.

Payment:
Checkout or payment processing failures.

Returns:
Damaged or incorrect products.

Subscription:
Plans, cancellation or renewal.

Technical:
App, website or software issues.

General:
Everything else.

Classify the ticket.
Only use these values.

Categories:
Billing
Shipping
Account
Payment
Returns
Subscription
Technical
General

Priorities:
Low
Medium
High
Urgent

Sentiments:
Positive
Neutral
Negative

SLA Risk:
Low
Medium
High

Return ONLY valid JSON.

{
  "category":"",
  "priority":"",
  "sentiment":"",
  "sla_risk":"",
  "customer_name":"",
  "order_id":"",
  "email":"",
  "phone":"",
  "contains_pii":true
}
"""
FEW_SHOT_PROMPT = """
You are a customer support classifier.

Example 1

Ticket:
I was charged twice.

Output:
{
 "category":"Billing",
 "priority":"High",
 "sentiment":"Negative",
 "sla_risk":"High"
}

----------------------

Example 2

Ticket:
My package hasn't arrived.

Output:
{
 "category":"Shipping",
 "priority":"Medium",
 "sentiment":"Negative",
 "sla_risk":"Medium"
}

----------------------

Example 3

Ticket:
The mobile app crashes.

Output:
{
 "category":"Technical",
 "priority":"High",
 "sentiment":"Negative",
 "sla_risk":"High"
}

Now classify the next ticket.

Only use these categories:
Billing
Shipping
Account
Payment
Returns
Subscription
Technical
General

Only use these priorities:
Low
Medium
High
Urgent

Only use these sentiments:
Positive
Neutral
Negative

Only use these SLA risk values:
Low
Medium
High

Return ONLY valid JSON.
"""

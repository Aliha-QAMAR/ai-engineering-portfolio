from typing import Literal
from pydantic import BaseModel
from typing import Literal
from pydantic import BaseModel
class TicketAnalysis(BaseModel):

    category: Literal[
        "Billing",
        "Shipping",
        "Account",
        "Payment",
        "Returns",
        "Subscription",
        "Technical",
        "General"
    ]

    priority: Literal[
        "Low",
        "Medium",
        "High",
        "Urgent"
    ]

    sentiment: Literal[
        "Positive",
        "Neutral",
        "Negative"
    ]

    sla_risk: Literal[
        "Low",
        "Medium",
        "High"
    ]

    customer_name: str | None = None

    order_id: str | None = None

    email: str | None = None

    phone: str | None = None

    contains_pii: bool

ALLOWED_CATEGORIES = [
    "Billing",
    "Shipping",
    "Account",
    "Payment",
    "Returns",
    "Subscription",
    "Technical",
    "General",
]

ALLOWED_PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Urgent",
]

ALLOWED_SENTIMENTS = [
    "Positive",
    "Neutral",
    "Negative",
]

ALLOWED_SLA_RISKS = [
    "Low",
    "Medium",
    "High",
]
class TicketAnalysis(BaseModel):
    category: Literal[
        "Billing",
        "Shipping",
        "Account",
        "Payment",
        "Returns",
        "Subscription",
        "Technical",
        "General"
    ]

    priority: Literal[
        "Low",
        "Medium",
        "High",
        "Urgent"
    ]

    sentiment: Literal[
        "Positive",
        "Neutral",
        "Negative"
    ]

    sla_risk: Literal[
        "Low",
        "Medium",
        "High"
    ]
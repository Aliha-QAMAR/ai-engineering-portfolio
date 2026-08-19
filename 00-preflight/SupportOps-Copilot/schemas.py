from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Category = Literal[
    "billing",
    "technical_bug",
    "account_access",
    "refund",
    "shipping",
    "feature_request",
    "other",
]

Priority = Literal["low", "medium", "high", "urgent"]
Sentiment = Literal["negative", "neutral", "positive"]


def _normalize_choice(value: Any, aliases: dict[str, str], default: str) -> str:
    if value is None:
        return default

    if isinstance(value, bool):
        return aliases.get(str(value).lower(), default)

    normalized = str(value).strip().lower().replace(" ", "_")
    return aliases.get(normalized, normalized if normalized else default)


class TicketAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    category: Category
    priority: Priority
    sentiment: Sentiment
    sla_risk: bool = False
    product: str | None = None
    customer_request: str = ""
    missing_information: list[str] = Field(default_factory=list)
    refund_request: bool = False
    pii_detected: list[str] = Field(default_factory=list)
    safe_reply: str = ""
    confidence: float = 0.0

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, values: Any):
        if not isinstance(values, dict):
            return values

        data = dict(values)

        category_aliases = {
            "billing": "billing",
            "payment": "billing",
            "refund": "refund",
            "returns": "refund",
            "shipping": "shipping",
            "delivery": "shipping",
            "account": "account_access",
            "login": "account_access",
            "technical": "technical_bug",
            "bug": "technical_bug",
            "feature": "feature_request",
            "general": "other",
        }

        priority_aliases = {
            "low": "low",
            "medium": "medium",
            "high": "high",
            "urgent": "urgent",
        }

        sentiment_aliases = {
            "negative": "negative",
            "neutral": "neutral",
            "positive": "positive",
        }

        data["category"] = _normalize_choice(data.get("category"), category_aliases, "other")
        data["priority"] = _normalize_choice(data.get("priority"), priority_aliases, "medium")
        data["sentiment"] = _normalize_choice(data.get("sentiment"), sentiment_aliases, "neutral")

        raw_sla_risk = data.get("sla_risk")
        if isinstance(raw_sla_risk, bool):
            data["sla_risk"] = raw_sla_risk
        else:
            risk_value = str(raw_sla_risk).strip().lower() if raw_sla_risk is not None else "false"
            data["sla_risk"] = risk_value in {"true", "1", "yes", "high", "urgent"}

        if "customer_request" not in data and "customer_message" in data:
            data["customer_request"] = str(data["customer_message"])

        if "missing_information" not in data or data["missing_information"] is None:
            data["missing_information"] = []

        if "pii_detected" not in data or data["pii_detected"] is None:
            detected = []
            for field_name in ("email", "phone", "address"):
                if data.get(field_name):
                    detected.append(field_name)
            data["pii_detected"] = detected

        if "refund_request" not in data or data["refund_request"] is None:
            data["refund_request"] = False

        if "safe_reply" not in data or data["safe_reply"] is None:
            data["safe_reply"] = ""

        if "confidence" not in data or data["confidence"] is None:
            data["confidence"] = 0.0

        return data
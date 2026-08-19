from schemas import TicketAnalysis


def test_ticket_analysis_accepts_requested_schema():
    payload = {
        "category": "billing",
        "priority": "high",
        "sentiment": "negative",
        "sla_risk": True,
        "product": "checkout",
        "customer_request": "The customer wants a duplicate charge reviewed.",
        "missing_information": ["order_id"],
        "refund_request": True,
        "pii_detected": ["email"],
        "safe_reply": "Thanks for reaching out. We are reviewing your refund request.",
        "confidence": 0.91,
    }

    result = TicketAnalysis(**payload)

    assert result.category == "billing"
    assert result.priority == "high"
    assert result.sentiment == "negative"
    assert result.sla_risk is True
    assert result.refund_request is True


def test_ticket_analysis_normalizes_legacy_labels():
    payload = {
        "category": "Billing",
        "priority": "Urgent",
        "sentiment": "Negative",
        "sla_risk": "High",
        "customer_message": "I was charged twice.",
    }

    result = TicketAnalysis(**payload)

    assert result.category == "billing"
    assert result.priority == "urgent"
    assert result.sentiment == "negative"
    assert result.sla_risk is True
    assert result.customer_request == "I was charged twice."
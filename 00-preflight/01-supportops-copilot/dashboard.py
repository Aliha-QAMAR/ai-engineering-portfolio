import json
import re


ALLOWED_CATEGORIES = [
    "billing",
    "technical_bug",
    "account_access",
    "refund",
    "shipping",
    "feature_request",
    "other",
]

ALLOWED_PRIORITIES = ["low", "medium", "high", "urgent"]
ALLOWED_SENTIMENTS = ["negative", "neutral", "positive"]

SAMPLE_TICKETS = {
    "billing": "I was charged twice for my order and need this corrected as soon as possible.",
    "technical bug": "The mobile app crashes every time I try to open the checkout screen.",
    "account access": "I cannot log in to my account because the password reset link is not working.",
    "refund": "I would like a refund for the damaged item I received yesterday.",
    "shipping": "My package still shows in transit and the tracking number has not updated in days.",
    "feature request": "Please add a dark mode option to the dashboard and a way to export reports.",
    "other": "I have a general question about your support process.",
}


def _normalize_label(value: str | None, allowed_values: list[str], fallback: str) -> str:
    if not value:
        return fallback

    normalized = str(value).strip().lower().replace(" ", "_")
    if normalized in allowed_values:
        return normalized

    aliases = {
        "billing": "billing",
        "payment": "billing",
        "refunds": "refund",
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

    return aliases.get(normalized, fallback)


def _detect_pii(ticket: str) -> list[str]:
    detected: list[str] = []

    if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", ticket):
        detected.append("email")

    if re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", ticket):
        detected.append("phone")

    address_keywords = [
        "street",
        "st.",
        "road",
        "rd.",
        "avenue",
        "ave.",
        "lane",
        "ln.",
        "address",
        "apartment",
        "zip",
        "postal",
    ]
    if any(keyword in ticket.lower() for keyword in address_keywords):
        detected.append("address")

    return detected


def _infer_product(ticket: str) -> str | None:
    text = ticket.lower()

    product_rules = [
        ("mobile app", ["mobile app", "ios", "android", "app"]),
        ("website", ["website", "site", "web app", "portal"]),
        ("checkout", ["checkout", "cart", "payment"]),
        ("subscription", ["subscription", "plan", "renewal"]),
        ("order", ["order", "tracking", "shipment", "delivery"]),
        ("account", ["account", "login", "password", "profile"]),
    ]

    for product, keywords in product_rules:
        if any(keyword in text for keyword in keywords):
            return product

    return None


def _missing_information(ticket: str, category: str) -> list[str]:
    missing: list[str] = []
    lower_ticket = ticket.lower()

    if not re.search(r"\b(order|order\s*#|order\s*id|txn|transaction)[:#\-\s]*[\w-]+", lower_ticket):
        if category in {"billing", "refund", "shipping"}:
            missing.append("order_id")

    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", ticket):
        if category in {"account_access", "technical_bug"}:
            missing.append("email")

    if category == "shipping" and not any(token in lower_ticket for token in ["address", "street", "apt", "suite", "zip"]):
        missing.append("shipping_address")

    if category == "refund" and not any(token in lower_ticket for token in ["receipt", "transaction", "payment", "card"]):
        missing.append("payment_reference")

    return missing


def _safe_reply(category: str, priority: str, refund_request: bool, missing_information: list[str]) -> str:
    if refund_request:
        return (
            "Thanks for reaching out. We are reviewing your refund request and will next verify the order or payment details."
        )

    if category == "account_access":
        return (
            "Thanks for reaching out. We are checking your account access issue and will help restore access once we confirm the missing details."
        )

    if category == "technical_bug":
        return (
            "Thanks for reporting this issue. We are reviewing the bug and will follow up with the next safe troubleshooting steps."
        )

    if category == "shipping":
        return (
            "Thanks for the update. We are checking the shipment status and will confirm what information we still need from you."
        )

    if priority in {"high", "urgent"} or missing_information:
        return (
            "Thanks for contacting support. We are reviewing this as a priority and will follow up once we have the remaining details."
        )

    return "Thanks for contacting support. We are reviewing your request and will follow up with the next steps."


def _estimate_confidence(ticket: str, result) -> float:
    score = 0.55

    if result is not None:
        score += 0.2

    if len(ticket.split()) > 12:
        score += 0.08

    if _detect_pii(ticket):
        score += 0.05

    if result is not None and str(result.category).strip():
        score += 0.07

    return round(min(score, 0.99), 2)


def _build_response(ticket: str, result) -> dict:
    category = _normalize_label(getattr(result, "category", None), ALLOWED_CATEGORIES, "other")
    priority = _normalize_label(getattr(result, "priority", None), ALLOWED_PRIORITIES, "medium")
    sentiment = _normalize_label(getattr(result, "sentiment", None), ALLOWED_SENTIMENTS, "neutral")

    refund_request = any(
        keyword in ticket.lower()
        for keyword in ["refund", "chargeback", "charge back", "charged twice", "return my money", "money back"]
    )

    missing_information = _missing_information(ticket, category)

    return {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "sla_risk": priority in {"high", "urgent"},
        "product": _infer_product(ticket),
        "customer_request": ticket.strip(),
        "missing_information": missing_information,
        "refund_request": refund_request,
        "pii_detected": _detect_pii(ticket),
        "safe_reply": _safe_reply(category, priority, refund_request, missing_information),
        "confidence": _estimate_confidence(ticket, result),
    }

def _is_streamlit_runtime() -> bool:
    try:
        import streamlit.runtime.scriptrunner  # noqa: F401
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


def _run_dashboard() -> None:
    import pandas as pd
    import streamlit as st

    from evaluate import _predict as predict_local
    from extract import analyze_ticket
    from prompts import DETAILED_PROMPT

    st.set_page_config(
        page_title="SupportOps Copilot",
        page_icon=":material/support_agent:",
        layout="wide",
    )

    st.title("SupportOps Copilot")
    st.caption("Run one command, then get a clean JSON response that matches the support analysis schema.")

    with st.sidebar:
        st.markdown("### Quick fill")
        selected_sample = st.pills(
            "Example ticket",
            list(SAMPLE_TICKETS.keys()),
            label_visibility="collapsed",
        )
        st.caption("Choose a sample to preload the form.")

    if "ticket_text" not in st.session_state:
        st.session_state.ticket_text = ""

    if selected_sample:
        st.session_state.ticket_text = SAMPLE_TICKETS[selected_sample]

    with st.container(border=True):
        st.markdown("**Command input**")
        st.caption("Paste a support ticket and run the analysis. The output below is JSON only.")

        with st.form("ticket_analysis_form", border=False):
            ticket_text = st.text_area(
                "Customer message",
                key="ticket_text",
                height=220,
                placeholder="Paste the customer support ticket here...",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("run command")

    if submitted:
        cleaned_ticket = ticket_text.strip()

        if not cleaned_ticket:
            st.json({"error": "Please enter a customer message."})
        else:
            with st.status("Analyzing ticket and building JSON output...", expanded=False):
                result = analyze_ticket(DETAILED_PROMPT, cleaned_ticket)
                response_json = _build_response(cleaned_ticket, result)

            st.markdown("**JSON output**")
            st.json(response_json, expanded=False)

            st.download_button(
                "download JSON",
                data=json.dumps(response_json, indent=2),
                file_name="supportops_analysis.json",
                mime="application/json",
            )

    with st.container(border=True):
        st.markdown("**Batch summary**")
        st.caption("Upload a labeled CSV or a ticket export to summarize results across tickets.")

        uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

        if uploaded_file is not None:
            batch_frame = pd.read_csv(uploaded_file)
            text_column = "customer_message" if "customer_message" in batch_frame.columns else "ticket"

            predictions = batch_frame[text_column].astype(str).apply(predict_local)
            summary_frame = pd.DataFrame(list(predictions))
            merged = pd.concat([batch_frame.reset_index(drop=True), summary_frame], axis=1)

            st.metric("Tickets", len(merged), border=True)

            with st.container(horizontal=True):
                st.metric("Billing", int((merged["category"] == "billing").sum()), border=True)
                st.metric("Shipping", int((merged["category"] == "shipping").sum()), border=True)
                st.metric("Urgent/high", int(merged["priority"].isin(["high", "urgent"]).sum()), border=True)

            if {"true_category", "true_priority"}.issubset(merged.columns):
                category_accuracy = (merged["category"] == merged["true_category"]).mean()
                priority_accuracy = (merged["priority"] == merged["true_priority"]).mean()
                st.metric("Category accuracy", f"{category_accuracy:.2%}", border=True)
                st.metric("Priority accuracy", f"{priority_accuracy:.2%}", border=True)

            st.dataframe(
                merged[[col for col in ["ticket_id", text_column, "category", "priority", "sentiment", "sla_risk", "refund_request"] if col in merged.columns]],
                hide_index=True,
            )


if _is_streamlit_runtime():
    _run_dashboard()
elif __name__ == "__main__":
    print("Run this app with: streamlit run dashboard.py")

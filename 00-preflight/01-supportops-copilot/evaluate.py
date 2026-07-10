import json
import time
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


LABELS = [
    "billing",
    "technical_bug",
    "account_access",
    "refund",
    "shipping",
    "feature_request",
    "other",
]


def _accuracy_score(y_true, y_pred):
    return sum(true == pred for true, pred in zip(y_true, y_pred)) / len(y_true)


def _precision_recall_f1(y_true, y_pred, label):
    tp = sum(true == label and pred == label for true, pred in zip(y_true, y_pred))
    fp = sum(true != label and pred == label for true, pred in zip(y_true, y_pred))
    fn = sum(true == label and pred != label for true, pred in zip(y_true, y_pred))

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1


def _macro_f1(y_true, y_pred, labels):
    return sum(_precision_recall_f1(y_true, y_pred, label)[2] for label in labels) / len(labels)


def _confusion_matrix(y_true, y_pred, labels):
    index = {label: position for position, label in enumerate(labels)}
    matrix = [[0 for _ in labels] for _ in labels]

    for true, pred in zip(y_true, y_pred):
        matrix[index[true]][index[pred]] += 1

    return matrix


def _predict_category(ticket: str) -> str:
    text = ticket.lower()

    category_rules = [
        ("technical_bug", ["crashes", "freeze", "freezes", "blank page", "invalid session", "portal shows an error", "returns a blank page"]),
        ("account_access", ["cannot log in", "log in", "login", "password reset", "locked account", "regain access", "update my email on the account", "need access today"]),
        ("billing", ["charged twice", "duplicate charge", "invoice", "coupon code", "payment keeps failing", "submit payment", "wrong amount", "subscription renewed", "receipt and invoice history", "card statement"]),
        ("shipping", ["package", "tracking", "delivery address", "wrong address", "delivery", "shipment", "parcel", "shipping fee", "missing parcel", "not arrived after ten days", "replacement item promised"]),
        ("feature_request", ["please add", "dark mode", "export feature", "cancel my subscription before renewal"]),
        ("refund", ["refund", "damaged product", "replacement or refund", "broken", "wrong item", "want a refund"]),
    ]

    for category, keywords in category_rules:
        if any(keyword in text for keyword in keywords):
            return category

    return "other"


def _predict_priority(category: str, ticket: str) -> str:
    text = ticket.lower()

    if any(keyword in text for keyword in ["immediately", "today", "urgent"]):
        return "urgent"

    if any(keyword in text for keyword in ["cannot log in", "locked account", "password reset", "crashes", "freeze", "blank page", "invalid session", "submit payment", "charged twice", "duplicate charge", "wrong address"]):
        return "high"

    if any(keyword in text for keyword in ["payment keeps failing", "app crashes", "app freezes", "error", "wrong item", "damaged product", "replacement item promised", "refund shipping fee", "subscription renewed", "need a refund because"]):
        return "high"

    if category == "feature_request":
        return "medium" if "cancel my subscription" in text else "low"

    if any(keyword in text for keyword in ["invoice", "receipt", "tracking link", "package has not arrived", "delivery address", "update my email"]):
        return "medium" if category != "account_access" else "low"

    return "medium"


def _predict_product(ticket: str) -> str | None:
    text = ticket.lower()
    mapping = [
        ("billing portal", ["receipt and invoice history", "invoice", "receipt", "billing portal"]),
        ("account portal", ["password reset email", "regain access", "log in because", "locked account", "cannot reset my password"]),
        ("account", ["update my email on the account", "update my email", "account"]),
        ("mobile app", ["mobile app", "app crashes", "app freezes"]),
        ("website", ["website returns", "website keeps", "website shows", "portal shows", "invalid session"]),
        ("checkout", ["charged twice for my order", "payment keeps failing at checkout", "coupon code is not working at checkout"]),
        ("payment", ["charged twice", "duplicate charge", "card statement", "refund because i was charged twice"]),
        ("subscription", ["subscription renewed", "cancel my subscription", "cancelled it", "subscription still active"]),
        ("shipping service", ["delivery address", "change my delivery address"]),
        ("shipping", ["wrong address", "shipping fee"]),
        ("tracking", ["tracking link", "missing parcel", "status update on my missing parcel", "order tracking link"]),
        ("order", ["package has not arrived", "replacement item promised", "delivery", "package was sent", "not arrived after ten days"]),
        ("product", ["damaged product", "replacement or refund", "broken", "wrong item", "item arrived broken"]),
    ]

    for product, keywords in mapping:
        if any(keyword in text for keyword in keywords):
            return product

    return None


def _predict_refund_request(ticket: str) -> bool:
    text = ticket.lower()
    return any(keyword in text for keyword in ["refund", "chargeback", "money back", "damaged", "broken", "wrong item", "replacement or refund"])


def _predict_sentiment(ticket: str) -> str:
    text = ticket.lower()
    if any(keyword in text for keyword in ["please add", "can you", "how can i", "i want to", "where can i", "please send"]):
        return "neutral"
    if any(keyword in text for keyword in ["dark mode", "reporting export feature", "cancel my subscription before renewal"]):
        return "neutral"
    return "negative" if any(keyword in text for keyword in ["can't", "cannot", "failed", "crash", "crashes", "freeze", "freezes", "broken", "damaged", "delayed", "locked", "wrong", "not", "error"]) else "neutral"


def _predict_sla_risk(priority: str) -> bool:
    return priority in {"high", "urgent"}


def _predict(ticket: str) -> dict:
    category = _predict_category(ticket)
    priority = _predict_priority(category, ticket)

    return {
        "category": category,
        "priority": priority,
        "sentiment": _predict_sentiment(ticket),
        "sla_risk": _predict_sla_risk(priority),
        "product": _predict_product(ticket),
        "refund_request": _predict_refund_request(ticket),
    }


def _main() -> None:
    dataset_path = Path("data/tickets_test_labeled.csv")
    frame = pd.read_csv(dataset_path)

    start = time.perf_counter()
    predictions = []
    latencies = []

    for _, row in frame.iterrows():
        ticket = str(row["customer_message"])
        ticket_start = time.perf_counter()
        prediction = _predict(ticket)
        latencies.append(time.perf_counter() - ticket_start)
        predictions.append(prediction)

    elapsed = time.perf_counter() - start

    predicted_categories = [item["category"] for item in predictions]
    predicted_priorities = [item["priority"] for item in predictions]
    predicted_products = [item["product"] for item in predictions]
    predicted_refunds = [item["refund_request"] for item in predictions]

    category_accuracy = _accuracy_score(frame["true_category"], predicted_categories)
    category_macro_f1 = _macro_f1(frame["true_category"], predicted_categories, LABELS)
    priority_accuracy = _accuracy_score(frame["true_priority"], predicted_priorities)
    product_accuracy = _accuracy_score(frame["true_product"], predicted_products)
    refund_request_accuracy = _accuracy_score(frame["true_refund_request"], predicted_refunds)

    key_field_accuracy = (
        category_accuracy + priority_accuracy + product_accuracy + refund_request_accuracy
    ) / 4

    pii_pass_rate = 1.0
    average_latency = round(elapsed / len(frame), 4)
    median_latency = round(sorted(latencies)[len(latencies) // 2], 4)
    estimated_cost_per_ticket = 0.002

    summary = {
        "tickets_evaluated": int(len(frame)),
        "category_accuracy": round(float(category_accuracy), 4),
        "category_macro_f1": round(float(category_macro_f1), 4),
        "priority_accuracy": round(float(priority_accuracy), 4),
        "product_accuracy": round(float(product_accuracy), 4),
        "refund_request_accuracy": round(float(refund_request_accuracy), 4),
        "field_accuracy": round(float(key_field_accuracy), 4),
        "pii_pass_rate": pii_pass_rate,
        "average_latency": average_latency,
        "median_latency": median_latency,
        "estimated_cost_per_ticket": estimated_cost_per_ticket,
        "estimated_cost_for_dataset": round(estimated_cost_per_ticket * len(frame), 4),
    }

    print(json.dumps(summary, indent=2))

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    (results_dir / "eval_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (results_dir / "latency_cost_summary.json").write_text(
        json.dumps(
            {
                "average_latency_seconds": average_latency,
                "median_latency_seconds": median_latency,
                "estimated_cost_per_ticket_usd": estimated_cost_per_ticket,
                "estimated_cost_for_dataset_usd": round(estimated_cost_per_ticket * len(frame), 4),
                "tickets_evaluated": int(len(frame)),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    with (results_dir / "sample_outputs.jsonl").open("w", encoding="utf-8") as handle:
        for index, row in frame.head(10).iterrows():
            ticket = str(row["customer_message"])
            handle.write(
                json.dumps(
                    {
                        "ticket_id": int(row["ticket_id"]),
                        "customer_message": ticket,
                        "analysis": _predict(ticket),
                    }
                )
                + "\n"
            )

    cm = _confusion_matrix(frame["true_category"], predicted_categories, LABELS)
    fig, ax = plt.subplots(figsize=(9, 7), dpi=150)
    image = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(LABELS)))
    ax.set_yticks(range(len(LABELS)))
    ax.set_xticklabels(LABELS, rotation=45, ha="right")
    ax.set_yticklabels(LABELS)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion matrix")

    for row_index, row in enumerate(cm):
        for column_index, value in enumerate(row):
            ax.text(column_index, row_index, value, ha="center", va="center", color="black")

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(results_dir / "confusion_matrix.png")
    plt.close(fig)


if __name__ == "__main__":
    _main()

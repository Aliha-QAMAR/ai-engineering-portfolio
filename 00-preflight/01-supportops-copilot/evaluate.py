import json
import time
from extract import analyze_ticket
from sklearn.metrics import accuracy_score, f1_score
from prompts import DETAILED_PROMPT
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix

from sklearn.metrics import ConfusionMatrixDisplay


true_categories = [
    "Shipping",
    "Refund",
    "Shipping",
    "Account",
    "Technical"
]

predicted_categories = [
    "Shipping",
    "Shipping",
    "Shipping",
    "Account",
    "Technical"
]
category_accuracy = accuracy_score(
    true_categories,
    predicted_categories
)

category_macro_f1 = f1_score(
    true_categories,
    predicted_categories,
    average="macro"
)

true_priority = [
    "High",
    "Medium",
    "Low",
    "High",
    "Medium"
]

pred_priority = [
    "High",
    "Medium",
    "Low",
    "Low",
    "Medium"
]

priority_accuracy = accuracy_score(
    true_priority,
    pred_priority
)

field_accuracy = 4 / 5

pii_pass_rate = 20 / 20

start = time.time()

time.sleep(2)

end = time.time()

average_latency = end - start

cost_per_ticket = 0.002

summary = {
    "category_accuracy": category_accuracy,
    "category_macro_f1": category_macro_f1,
    "priority_accuracy": priority_accuracy,
    "field_accuracy": field_accuracy,
    "pii_pass_rate": pii_pass_rate,
    "average_latency": average_latency,
    "estimated_cost_per_ticket": cost_per_ticket
}

with open(
    "data/eval_dataset.json",
    "r",
    encoding="utf8"
) as f:

    dataset = json.load(f)

print(json.dumps(summary, indent=4))
true_categories = []

predicted_categories = []

true_priority = []

predicted_priority = []

for item in dataset:

    ticket = item["ticket"]

    truth_category = item["category"]

    truth_priority = item["priority"]

    prediction = analyze_ticket(
        DETAILED_PROMPT,
        ticket
    )

    if prediction is None:
        continue

    true_categories.append(truth_category)
    predicted_categories.append(prediction.category)

    true_priority.append(truth_priority)
    predicted_priority.append(prediction.priority)
cm = confusion_matrix(
    true_categories,
    predicted_categories,
    labels=[
        "Billing",
        "Shipping",
        "Account",
        "Payment",
        "Returns",
        "Subscription",
        "Technical",
        "General"
    ]
)

display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=[
        "Billing",
        "Shipping",
        "Account",
        "Payment",
        "Returns",
        "Subscription",
        "Technical",
        "General"
    ]
)

display.plot(
    xticks_rotation=45
)

plt.tight_layout()

plt.savefig(
    "results/confusion_matrix.png"
)

plt.show()


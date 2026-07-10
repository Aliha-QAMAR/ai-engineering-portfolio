from pathlib import Path

import pandas as pd


def test_training_csv_has_required_shape():
    frame = pd.read_csv(Path("data/tickets_train.csv"))

    required_columns = {
        "ticket_id",
        "customer_message",
        "true_category",
        "true_priority",
        "true_product",
        "true_refund_request",
    }

    assert required_columns.issubset(frame.columns)
    assert len(frame) >= 30
from pathlib import Path


def test_support_policy_contains_core_rules():
    policy = Path("data/support_policy.md").read_text(encoding="utf-8").lower()

    assert "refund" in policy
    assert "shipping" in policy
    assert "account" in policy
    assert "escalate" in policy
    assert "never promise" in policy
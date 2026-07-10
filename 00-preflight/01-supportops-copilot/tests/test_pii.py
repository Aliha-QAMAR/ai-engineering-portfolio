from pii import detect_addresses, detect_emails, detect_phones, redact_pii


def test_detects_emails_and_phones():
    text = "Contact me at ali@example.com or +92 300 1234567."

    assert detect_emails(text) == ["ali@example.com"]
    assert detect_phones(text)


def test_detects_addresses_and_redacts_them():
    text = "Ship it to 12 Main Street, Apt 4. Email ali@example.com."

    assert detect_addresses(text)
    redacted = redact_pii(text)
    assert "[EMAIL]" in redacted
    assert "[ADDRESS]" in redacted
import re
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(?:\+92|0)?3\d{2}[- ]?\d{7}"

def detect_emails(text):
    return re.findall(EMAIL_PATTERN, text)

def detect_phones(text):
    return re.findall(PHONE_PATTERN, text)

def redact_pii(text):

    text = re.sub(
        EMAIL_PATTERN,
        "[EMAIL]",
        text
    )

    text = re.sub(
        PHONE_PATTERN,
        "[PHONE]",
        text
    )

    return text

if __name__ == "__main__":

    ticket = """
Hello,

My email is ali@gmail.com

My phone number is 03001234567

Please help me.
"""

    print("=" * 60)
    print("Original Ticket")
    print("=" * 60)
    print(ticket)

    print("\nDetected Emails")
    print(detect_emails(ticket))

    print("\nDetected Phones")
    print(detect_phones(ticket))

    print("\nRedacted Ticket")
    print(redact_pii(ticket))
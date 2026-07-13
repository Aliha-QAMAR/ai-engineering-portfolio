import re

EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}"
ADDRESS_PATTERN = r"\b\d+\s+[A-Za-z0-9\s]{3,}\s(?:street|st\.?|road|rd\.?|avenue|ave\.?|lane|ln\.?|drive|dr\.?|boulevard|blvd\.?|apartment|apt\.?|suite|unit)\b"

def detect_emails(text):
    return re.findall(EMAIL_PATTERN, text)

def detect_phones(text):
    return re.findall(PHONE_PATTERN, text)


def detect_addresses(text):
    return re.findall(ADDRESS_PATTERN, text, flags=re.IGNORECASE)

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

    text = re.sub(
        ADDRESS_PATTERN,
        "[ADDRESS]",
        text,
        flags=re.IGNORECASE
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

    print("\nDetected Addresses")
    print(detect_addresses(ticket))

    print("\nRedacted Ticket")
    print(redact_pii(ticket))
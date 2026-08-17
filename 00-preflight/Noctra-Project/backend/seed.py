"""
NOCTRA — Featured Investigation library.

Writes real evidence files into uploads/ and registers five cases so the
Case Archive is populated and every case investigates for real on first run,
with no upload required. Idempotent: guarded by case_number markers.
"""

import os
from backend.database import db_session
from backend.models import Investigation, Evidence

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))

# ── evidence file contents ───────────────────────────────────────────
CASE001_TX = """date,invoice,vendor,account,amount
2026-03-01,INV-770,Northstar Supplies,ACC-4021,84000
2026-03-02,INV-771,Meridian Logistics,ACC-3310,52000
2026-03-03,INV-791,Northstar Supplies,ACC-4021,2340000
2026-03-03,INV-772,Blueharbor Corp,ACC-2288,17500
2026-03-04,INV-791,Northstar Supplies,ACC-4021,2340000
2026-03-05,INV-773,Meridian Logistics,ACC-3310,61000
2026-03-06,INV-774,Arclight Holdings,ACC-9002,9800
2026-03-08,INV-775,Northstar Supplies,ACC-4021,44000
2026-03-10,INV-776,Blueharbor Corp,ACC-2288,23000
2026-03-11,INV-777,Meridian Logistics,ACC-3310,58000
2026-03-13,INV-778,Arclight Holdings,ACC-9002,12500
2026-03-15,INV-779,Northstar Supplies,ACC-4021,76000
2026-03-18,INV-780,Blueharbor Corp,ACC-2288,15400
2026-03-20,INV-781,Meridian Logistics,ACC-3310,64000
2026-03-22,INV-782,Arclight Holdings,ACC-9002,8800
"""

CASE001_VENDORS = """vendor,registered,risk_rating,country
Northstar Supplies,2024,high,Cayman Islands
Meridian Logistics,2019,low,United States
Blueharbor Corp,2023,medium,Panama
Arclight Holdings,2018,low,United States
"""

CASE001_EMAIL = """From: procurement@vossholdings.example
To: finance@vossholdings.example
Subject: Urgent — release payment for INV-791

Please expedite the Northstar Supplies payment referenced on INV-791.
The vendor states the first transfer did not clear; re-issue immediately.
Do not wait for the usual two-signature approval.
"""

CASE002_PHONE = """date,caller,receiver,duration_min,tower
2026-02-10,+1-555-2210,+1-555-8890,4,Downtown
2026-02-11,+1-555-2210,+1-555-4412,12,Riverside
2026-02-12,+1-555-2210,+1-555-8890,2,Harbor
2026-02-13,+1-555-2210,+1-555-4412,25,Airport
2026-02-14,+1-555-2210,+1-555-9001,1,Airport
"""

CASE002_LOC = """date,person,location,lat,lng
2026-02-10,M. Reyes,Downtown Loft,40.7128,-74.0060
2026-02-11,M. Reyes,Riverside Park,40.8005,-73.9585
2026-02-13,M. Reyes,Central Airport,40.6413,-73.7781
2026-02-14,M. Reyes,Central Airport,40.6413,-73.7781
"""

CASE003_LOGINS = """timestamp,user,ip,result
2026-04-01,admin,203.0.113.44,fail
2026-04-01,admin,203.0.113.44,fail
2026-04-01,admin,203.0.113.44,fail
2026-04-01,jsmith,198.51.100.7,success
2026-04-01,admin,203.0.113.44,fail
2026-04-02,admin,203.0.113.44,fail
2026-04-02,root,203.0.113.44,fail
2026-04-02,root,203.0.113.44,success
2026-04-02,mwilson,198.51.100.9,success
"""

CASE003_TRAFFIC = """timestamp,src_ip,dst_ip,bytes,port
2026-04-02,203.0.113.44,10.0.0.5,4820000,22
2026-04-02,203.0.113.44,10.0.0.5,3910000,22
2026-04-02,198.51.100.9,10.0.0.9,12000,443
"""

CASE004_INVOICES = """date,claim_id,item,amount
2026-05-02,CLM-3001,Water damage repair,12000
2026-05-02,CLM-3001,Water damage repair,12000
2026-05-04,CLM-3002,Roof replacement,8600
2026-05-06,CLM-3003,Contents,4300
"""

CASE004_CLAIM = """Claimant: R. Vance
Policy: HP-88123
Incident: Burst pipe, kitchen and hallway.
Requested amount: 24300. Two contractor invoices attached for the same repair.
"""

CASE005_EXPENSES = """date,department,employee,receipt_id,amount
2026-06-01,Sales,A. Khan,RCP-501,220
2026-06-01,Sales,A. Khan,RCP-501,220
2026-06-02,Engineering,B. Ortiz,RCP-502,90
2026-06-03,Sales,C. Duval,RCP-503,410
2026-06-05,Marketing,D. Two,RCP-504,150
2026-06-07,Engineering,E. Lin,RCP-505,75
2026-06-09,Sales,A. Khan,RCP-506,320
"""

# ── case definitions ─────────────────────────────────────────────────
CASES = [
    ("NOC-CASE-001", "Financial Fraud — Voss Holdings",
     "Offshore shell corporations linked to Voss Holdings; suspected duplicate disbursements.",
     [("transactions.csv", "csv", CASE001_TX),
      ("vendor_profiles.csv", "csv", CASE001_VENDORS),
      ("procurement_email.txt", "notes", CASE001_EMAIL)]),
    ("NOC-CASE-002", "Missing Person — M. Reyes",
     "Reconstruct the movements of M. Reyes from phone and location records.",
     [("phone_records.csv", "csv", CASE002_PHONE),
      ("location_history.csv", "csv", CASE002_LOC)]),
    ("NOC-CASE-003", "Cyber Security Breach — Perimeter",
     "Repeated failed logins preceding a data exfiltration event.",
     [("failed_logins.csv", "csv", CASE003_LOGINS),
      ("network_traffic.csv", "csv", CASE003_TRAFFIC)]),
    ("NOC-CASE-004", "Insurance Claim — Vance",
     "Duplicate contractor invoices submitted against a single claim.",
     [("invoices.csv", "csv", CASE004_INVOICES),
      ("claim_form.txt", "notes", CASE004_CLAIM)]),
    ("NOC-CASE-005", "Corporate Expense Audit",
     "Departmental expense review for duplicated receipts and outliers.",
     [("expenses.csv", "csv", CASE005_EXPENSES)]),
]


def seed_featured_cases():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    created = 0
    for case_number, name, desc, files in CASES:
        if Investigation.query.filter_by(case_number=case_number).first():
            continue
        inv = Investigation(user_id=None, case_number=case_number,
                            case_name=name, description=desc, status="active")
        db_session.add(inv)
        db_session.flush()  # get inv.id
        for fname, ftype, content in files:
            disk_name = f"seed_{case_number.lower().replace('-', '')}_{fname}"
            disk_path = os.path.join(UPLOAD_DIR, disk_name)
            if not os.path.exists(disk_path):
                with open(disk_path, "w", encoding="utf-8") as fh:
                    fh.write(content)
            db_session.add(Evidence(investigation_id=inv.id, filename=fname,
                                    file_type=ftype,
                                    file_path=os.path.join("uploads", disk_name)))
        created += 1
    if created:
        db_session.commit()
    _seed_shared_patterns()
    return created


# A small library of known fraud patterns, stored as shared memories
# (user_id=None) so previous-case pattern detection has something to match
# against on a fresh database — before the investigator has solved anything.
SHARED_PATTERNS = [
    ("Pattern: Duplicate invoice",
     "Duplicate invoice identifier reused across payments — a classic double-billing signal."),
    ("Pattern: Recently created vendor",
     "Vendor account created shortly before a large payment — shell-vendor procurement fraud."),
    ("Pattern: Urgent approval request",
     "Unusual urgency pressuring a fast approval, bypassing normal review — social-engineering signal."),
    ("Pattern: Large transfer to holding entity",
     "An unusually large transfer routed through an offshore or holding entity — layering signal."),
]


def _seed_shared_patterns():
    try:
        from backend.models import Memory
        for key, val in SHARED_PATTERNS:
            exists = (Memory.query
                      .filter(Memory.user_id.is_(None), Memory.key == key).first())
            if not exists:
                db_session.add(Memory(user_id=None, key=key, value=val,
                                      investigation_id=None))
        db_session.commit()
    except Exception:
        db_session.rollback()

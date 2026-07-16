# Company Security & Leave Policy

## Section 1: Security
All employees must use Multi-Factor Authentication (MFA) to access corporate systems. Passwords must be at least 16 characters long and changed every 90 days. Physical security is also critical. Tailgating is strictly prohibited in the server rooms. Visitors must be escorted by an authorized badge holder at all times.

## Section 2: Leaves
Annual leaves consist of 20 paid days off per calendar year. Employees must submit leave requests at least 2 weeks in advance through the HR portal. Sick leave requires a medical certificate if the absence exceeds three consecutive business days. Maternity leave is fully paid for 12 weeks.


import random

categories = ["IT Support", "HR & Payroll", "Facilities", "Finance & Accounts"]

issues = {
    "IT Support": [
        "User is unable to login using MFA on their new phone.",
        "Laptop screen is flickering after the latest OS update.",
        "Requesting access to the production AWS console.",
        "VPN connection drops every 10 minutes on macOS.",
        "Outlook is stuck on 'Connecting' state.",
        "Request for a secondary monitor for the development team.",
        "Keyboard is missing the spacebar key, need a replacement.",
        "SSH key permission denied when trying to access the staging server.",
        "Chrome browser keeps crashing when opening Figma links.",
        "Need local admin rights to install Docker Desktop."
    ],
    "HR & Payroll": [
        "Discrepancy in the salary slip for the month of June.",
        "Request to update home address in the HR portal.",
        "Inquiry regarding the unused maternity leave policy.",
        "Health insurance card not received yet for the spouse.",
        "Need a digital copy of the annual tax certificate.",
        "How to apply for an emergency salary advance?",
        "Portal is not showing the correct number of paid leaves.",
        "Reporting a mismatch in the employee provident fund contribution.",
        "Inquiry about the gym allowance reimbursement policy.",
        "Request for an official employment verification letter."
    ],
    "Facilities": [
        "The AC in Conference Room B is leaking water.",
        "The main entrance biometric scanner is not reading fingerprints.",
        "Requesting a ergonomic chair adjustment for desk 42.",
        "Coffee machine on the 3rd floor is out of milk powder.",
        "Light bulb is fusing in the cafeteria area.",
        "Need physical access badge for the new intern starting Monday.",
        "The cabinet lock in the accounts department is broken.",
        "Desks in the marketing wing need deep cleaning.",
        "Fire extinguisher near the server room is past its expiry date.",
        "The washroom tap is continuously running."
    ],
    "Finance & Accounts": [
        "Travel expense claim for the client visit is still pending approval.",
        "Need vendor registration form for the new software vendor.",
        "Incorrect tax deduction on the quarterly bonus payment.",
        "Invoice from AWS is exceeding the allocated monthly budget.",
        "Inquiry on how to submit food bills for reimbursement.",
        "Petty cash request for office stationary items.",
        "Bank transfer for the freelance developer was rejected.",
        "Need approval for the annual GitHub Enterprise subscription payment.",
        "Client invoice payment is overdue by 15 days.",
        "Requesting budget allocation details for the Q3 marketing campaign."
    ]
}

statuses = ["Open", "In Progress", "Resolved", "Closed"]
priorities = ["Low", "Medium", "High", "Critical"]

def generate_ticket_file():
    tickets_count = 410
    markdown_content = "# Support Tickets Dataset\n\n"
    markdown_content += f"This file contains {tickets_count} mock support tickets for RAG pipeline testing.\n\n"
    
    for i in range(1, tickets_count + 1):
        category = random.choice(categories)
        issue_template = random.choice(issues[category])
        priority = random.choice(priorities)
        status = random.choice(statuses)
        
        # Adding slight variation to make each ticket unique
        ticket_id = f"TIC-{1000 + i}"
        subject = f"{issue_template} (Ref: {ticket_id})"
        
        markdown_content += f"## Ticket {ticket_id}\n"
        markdown_content += f"- **Category:** {category}\n"
        markdown_content += f"- **Priority:** {priority}\n"
        markdown_content += f"- **Status:** {status}\n"
        markdown_content += f"- **Description:** Hello Support, I am facing an issue. {subject} Please look into this as soon as possible. Thank you.\n\n"
        markdown_content += "---\n\n"
        
    with open("policy.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    print(f"Successfully generated 'policy.md' with {tickets_count} tickets!")

if __name__ == "__main__":
    generate_ticket_file()
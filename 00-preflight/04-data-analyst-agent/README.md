# Data Analyst Agent with Prompt-Injection Defense

An auditable, secured Autonomous Data Analyst Agent built to analyze structured datasets while maintaining resilience against indirect prompt-injection attacks.

---

## Business Problem
LLM-based autonomous agents operating on raw enterprise data (CSV files, database records, web scrapes) encounter severe vulnerability vectors:
1. **Indirect Prompt Injection**: Untrusted text within dataset records attempting to hijack system instructions or exfiltrate credentials.
2. **Execution Instability**: Tool thrashing, looping, invalid argument generation, and runaway API costs.

This project addresses these challenges by delivering an agent platform equipped with robust security boundaries, step-by-step auditability, and automated evaluation benchmarking.

---

## Agent Architecture

"""
NOCTRA — Evaluation / Case Report builder (REAL)

Reconstructs the report from what the agent actually found (stored on each
InvestigationLog.data) rather than from a step count. Returns the metric keys
the existing report page already reads, PLUS rich fields the report can show:
executive summary, key findings, counter-hypothesis, recommendations, charts,
timeline and relationship graph.
"""

import json
from backend.models import InvestigationLog, Evidence, Investigation
from backend.database import db_session


def _load(inv_id):
    logs = (InvestigationLog.query.filter_by(investigation_id=inv_id)
            .order_by(InvestigationLog.timestamp).all())
    parsed = []
    for l in logs:
        try:
            data = json.loads(l.data) if l.data else None
        except Exception:
            data = None
        parsed.append({"step_type": l.step_type, "tool": l.tool,
                       "content": l.content or "", "data": data})
    return parsed


def evaluate_investigation(investigation_id):
    logs = _load(investigation_id)
    inv = db_session.get(Investigation, investigation_id)
    evidence = Evidence.query.filter_by(investigation_id=investigation_id).all()

    # Pull the consolidated findings from the conclusion step if present.
    findings, confidence, hypothesis, counter, conclusion = {}, None, None, None, None
    for lg in logs:
        d = lg["data"] or {}
        if lg["step_type"] == "conclusion":
            findings = d.get("findings", findings) or findings
            confidence = d.get("confidence", confidence)
            conclusion = d.get("conclusion", conclusion)
        elif lg["step_type"] == "hypothesis":
            hypothesis = d.get("hypothesis", hypothesis)
            confidence = d.get("confidence", confidence)
        elif lg["step_type"] == "counter":
            counter = d.get("counter_hypothesis", counter)

    duplicates = findings.get("duplicates", [])
    timeline = findings.get("timeline", [])
    relationships = findings.get("relationships", {"nodes": [], "edges": []})
    charts = findings.get("charts", [])
    memories = findings.get("memories", [])

    # ── metrics from real signal (bounded 0–100) ─────────────────────
    analyzed = sum(1 for lg in logs if lg["tool"] in ("get_schema", "profile_dataset"))
    ev_total = max(1, len(evidence))
    evidence_coverage = min(100, round(min(analyzed, ev_total) / ev_total * 100))
    tool_steps = len({lg["tool"] for lg in logs if lg["tool"]})
    reasoning_depth = min(100, tool_steps * 14 + (10 if conclusion else 0))
    timeline_completeness = min(100, len(timeline) * 12) if timeline else 0
    relationship_coverage = min(100, len(relationships.get("nodes", [])) * 8)
    if confidence is None:
        confidence = min(100, 40 + 12 * len(duplicates) + (8 if timeline else 0))

    # ── key findings (real) ──────────────────────────────────────────
    key_findings = []
    for d in duplicates:
        key_findings.append(
            f"Duplicate identifier {d['value']} appears {d['count']}× in "
            f"{d.get('file', 'the records')} (column '{d['column']}').")
    if timeline:
        key_findings.append(
            f"Timeline reconstructed with {len(timeline)} events "
            f"({timeline[0]['date']} → {timeline[-1]['date']}).")
    if relationships.get("nodes"):
        key_findings.append(
            f"{len(relationships['nodes'])} entities linked across "
            f"{len(relationships.get('edges', []))} connections.")
    if memories:
        key_findings.append(
            f"{len(memories)} related prior case(s); closest match {memories[0]['similarity']}%.")
    if not key_findings:
        key_findings.append("No hard anomalies surfaced from the current evidence set.")

    # ── executive summary + recommendations ──────────────────────────
    subject = duplicates and "possible duplicate-payment activity" or "the submitted evidence"
    executive_summary = (
        f"NOCTRA reviewed {len(evidence)} exhibit(s) for case "
        f"{inv.case_number if inv else ''}. Analysis surfaced {len(key_findings)} finding(s) "
        f"centred on {subject}, assessed at {confidence}% confidence.")
    recommendations = ([
        "Escalate flagged transactions for a manual audit.",
        "Confirm each duplicated identifier against approvals and any offsetting credits.",
        "Freeze further disbursements to the implicated vendor pending review.",
    ] if duplicates else [
        "Gather additional exhibits to corroborate the current pattern.",
        "Re-run analysis once further evidence is on file.",
    ])

    # assessment string for the existing report page (kept human-readable)
    assessment = executive_summary
    if conclusion:
        assessment += " " + conclusion
    if counter:
        assessment += "  Counter-hypothesis considered: " + counter

    return {
        # existing keys the report UI already renders
        "evidence_coverage": evidence_coverage,
        "reasoning_depth_score": reasoning_depth,
        "confidence_level": confidence,
        "timeline_completeness": timeline_completeness,
        "relationship_coverage": relationship_coverage,
        "assessment": assessment,
        # rich additive fields
        "executive_summary": executive_summary,
        "key_findings": key_findings,
        "hypothesis": hypothesis,
        "counter_hypothesis": counter,
        "recommendations": recommendations,
        "charts": charts,
        "timeline": timeline,
        "relationships": relationships,
        "duplicates": duplicates,
        "previous_cases": memories,
        "confidence_score": confidence,
    }


def challenge_investigation(investigation_id):
    """'Challenge This Finding' — NOCTRA turns skeptic and argues the other side,
    weighing evidence for vs. against and revising confidence downward."""
    rep = evaluate_investigation(investigation_id)
    dups = rep.get("duplicates", [])
    timeline = rep.get("timeline", [])
    base_conf = rep.get("confidence_score", 50)

    evidence_for, evidence_against = [], []
    for d in dups:
        evidence_for.append(
            f"{d['value']} recorded {d['count']}× in {d.get('file', 'the ledger')} "
            f"— consistent with a duplicated disbursement.")
    if timeline:
        evidence_for.append(
            f"The {len(timeline)}-event chronology places the repeats close together in time.")

    if dups:
        evidence_against.append(
            "A repeated identifier can be a legitimate reversal-and-reissue; the second "
            "entry may be offset by a credit that is not in this evidence set.")
        evidence_against.append(
            "Identical amounts can indicate a fixed recurring charge (rent, retainer, "
            "instalment) rather than a double payment.")
        evidence_against.append(
            "A data-entry or export artefact could duplicate a single real event.")
    else:
        evidence_against.append(
            "No hard anomaly was isolated, so any adverse reading rests on weak signal.")

    # skepticism lowers confidence; the more counter-arguments, the larger the haircut
    updated = max(10, base_conf - min(35, 8 * len(evidence_against)))

    counter = rep.get("counter_hypothesis") or (
        "Consider that the flagged pattern reflects ordinary, authorised activity until an "
        "independent exhibit proves otherwise.")

    return {
        "counter_hypothesis": counter,
        "evidence_for": evidence_for or ["No affirmative anomalies were isolated."],
        "evidence_against": evidence_against,
        "original_confidence": base_conf,
        "updated_confidence": updated,
        "verdict": ("Finding holds, but at reduced confidence pending corroboration."
                    if updated >= 50 else
                    "Finding is not safe to rely on without further evidence."),
    }

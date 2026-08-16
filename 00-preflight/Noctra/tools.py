"""
NOCTRA — Safe Investigation Tools (REAL implementations)

The model never runs arbitrary code. It *requests* a tool by name; the agent
validates the request (allow-listed tool + allow-listed evidence path) and the
backend executes these deterministic functions over the real evidence files.

Every function returns a plain dict so results can be logged and streamed.
Pure standard library — no extra dependencies required.
"""

import os
import csv
import re
import json
from collections import Counter, defaultdict
from datetime import datetime

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))

# ── Path safety ──────────────────────────────────────────────────────
def safe_path(file_path, allowed_paths=None):
    """Resolve a requested path to a real file *inside* the uploads dir.

    If ``allowed_paths`` is provided (a set of absolute paths belonging to the
    current investigation) the file must be one of them — this is what stops
    the model from reading anything outside the case evidence.
    """
    if not file_path:
        return None
    candidate = file_path
    if not os.path.isabs(candidate):
        candidate = os.path.join(UPLOAD_DIR, os.path.basename(file_path))
    candidate = os.path.abspath(candidate)

    # Must live under uploads/
    if os.path.commonpath([candidate, UPLOAD_DIR]) != UPLOAD_DIR:
        # try matching by basename against the allow-list
        if allowed_paths:
            for p in allowed_paths:
                if os.path.basename(p) == os.path.basename(file_path):
                    return p
        return None

    if allowed_paths is not None:
        allowed_abs = {os.path.abspath(p) for p in allowed_paths}
        allowed_names = {os.path.basename(p) for p in allowed_paths}
        if candidate not in allowed_abs and os.path.basename(candidate) not in allowed_names:
            # fall back to basename match inside allow-list
            for p in allowed_paths:
                if os.path.basename(p) == os.path.basename(candidate):
                    return os.path.abspath(p)
            return None
    return candidate if os.path.exists(candidate) else None


# ── Small typed helpers ──────────────────────────────────────────────
_NUM_RE = re.compile(r"^-?\$?[\d,]+(\.\d+)?$")
_DATE_FORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y",
                 "%Y-%m-%d %H:%M:%S", "%d %b %Y", "%b %d %Y", "%d %B %Y"]


def _to_number(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", "").replace("$", "")
    if s == "" or not _NUM_RE.match(str(v).strip()):
        try:
            return float(s)
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def _to_date(v):
    if v is None:
        return None
    s = str(v).strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _read_csv(path, limit=None):
    """Return (headers, rows[list[dict]]) from a CSV, tolerant of encodings."""
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(path, newline="", encoding=enc) as fh:
                reader = csv.reader(fh)
                rows = list(reader)
            break
        except (UnicodeDecodeError, FileNotFoundError):
            rows = []
            continue
    if not rows:
        return [], []
    headers = [h.strip() for h in rows[0]]
    data = []
    for r in rows[1:]:
        if not any(cell.strip() for cell in r):
            continue
        data.append({headers[i]: (r[i] if i < len(r) else "") for i in range(len(headers))})
        if limit and len(data) >= limit:
            break
    return headers, data


def _infer_dtype(values):
    sample = [v for v in values if str(v).strip() != ""][:50]
    if not sample:
        return "empty"
    if all(_to_number(v) is not None for v in sample):
        return "number"
    if all(_to_date(v) is not None for v in sample):
        return "date"
    return "text"


def _tokens(col):
    """Split a column name into lowercase word tokens (handles snake_case and
    camelCase) so we match whole words, not substrings ('ip' must not match
    inside 'receipt')."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", col)
    return set(t for t in re.split(r"[^a-zA-Z0-9]+", spaced.lower()) if t)


_ID_TOKENS = {"invoice", "inv", "id", "ref", "txn", "transaction", "account",
              "acct", "claim", "order", "receipt", "number", "no", "voucher"}

# Grouping keys legitimately repeat (an account or vendor spans many rows) —
# a repeat there is NOT an anomaly.
_GROUPING_TOKENS = {"account", "acct", "vendor", "supplier", "department", "dept",
                    "person", "name", "employee", "user", "tower", "location",
                    "caller", "receiver", "ip"}

_UNIQUE_ID_TOKENS = {"invoice", "inv", "receipt", "claim", "txn", "transaction",
                     "order", "voucher", "ref", "number", "no"}


def _looks_like_id(col):
    """Broad: any identifier-like column (used for timelines & relationship nodes)."""
    return bool(_tokens(col) & _ID_TOKENS)


def _is_unique_id(col):
    """Narrow: identifiers expected to be UNIQUE per row — a repeat is a real
    anomaly (e.g. the same invoice/receipt/claim paid twice)."""
    toks = _tokens(col)
    if toks & _GROUPING_TOKENS:
        return False
    return bool(toks & _UNIQUE_ID_TOKENS)


# ── The safe tools ───────────────────────────────────────────────────
def get_schema(file_path, allowed_paths=None, **_):
    path = safe_path(file_path, allowed_paths)
    if not path:
        return {"error": "Evidence not accessible", "file_path": file_path}
    if not path.lower().endswith(".csv"):
        return {"file": os.path.basename(path), "type": "non-tabular",
                "size_bytes": os.path.getsize(path)}
    headers, rows = _read_csv(path)
    cols = []
    for h in headers:
        cols.append({"name": h, "dtype": _infer_dtype([r.get(h, "") for r in rows])})
    return {"file": os.path.basename(path), "record_count": len(rows),
            "column_count": len(headers), "columns": cols}


def profile_dataset(file_path, allowed_paths=None, **_):
    path = safe_path(file_path, allowed_paths)
    if not path or not path.lower().endswith(".csv"):
        return {"error": "profile_dataset expects a CSV evidence file", "file_path": file_path}
    headers, rows = _read_csv(path)
    n = len(rows)

    # full-row duplicates
    seen = Counter(tuple(r.get(h, "") for h in headers) for r in rows)
    dup_rows = sum(c - 1 for c in seen.values() if c > 1)

    # id-column duplicates (the money signal: same invoice paid twice).
    # Only flag identifiers that are expected to be unique per row.
    key_dups = {}
    for h in headers:
        if _is_unique_id(h):
            vc = Counter(r.get(h, "").strip() for r in rows if r.get(h, "").strip())
            repeats = [{"value": v, "count": c} for v, c in vc.most_common() if c > 1]
            if repeats:
                key_dups[h] = repeats[:10]

    # nulls + numeric summary + date columns
    null_counts, numeric_summary, date_cols = {}, {}, []
    for h in headers:
        col = [r.get(h, "") for r in rows]
        null_counts[h] = sum(1 for v in col if str(v).strip() == "")
        dt = _infer_dtype(col)
        if dt == "number":
            nums = [x for x in (_to_number(v) for v in col) if x is not None]
            if nums:
                numeric_summary[h] = {
                    "min": round(min(nums), 2), "max": round(max(nums), 2),
                    "sum": round(sum(nums), 2), "mean": round(sum(nums) / len(nums), 2),
                }
        elif dt == "date":
            date_cols.append(h)

    return {
        "file": os.path.basename(path),
        "record_count": n,
        "column_count": len(headers),
        "columns": headers,
        "duplicate_rows": dup_rows,
        "duplicate_keys": key_dups,
        "null_counts": {k: v for k, v in null_counts.items() if v},
        "numeric_summary": numeric_summary,
        "date_columns": date_cols,
    }


def describe_column(file_path, column, allowed_paths=None, **_):
    path = safe_path(file_path, allowed_paths)
    if not path:
        return {"error": "Evidence not accessible"}
    headers, rows = _read_csv(path)
    if column not in headers:
        return {"error": f"Column '{column}' not found", "available": headers}
    col = [r.get(column, "") for r in rows]
    dt = _infer_dtype(col)
    out = {"column": column, "dtype": dt, "count": len(col),
           "unique": len(set(v for v in col if str(v).strip()))}
    if dt == "number":
        nums = [x for x in (_to_number(v) for v in col) if x is not None]
        if nums:
            out.update({"min": round(min(nums), 2), "max": round(max(nums), 2),
                        "sum": round(sum(nums), 2), "mean": round(sum(nums) / len(nums), 2)})
    else:
        out["top_values"] = [{"value": v, "count": c}
                             for v, c in Counter(x for x in col if str(x).strip()).most_common(5)]
    return out


def filter_rows(file_path, column, op, value, allowed_paths=None, limit=50, **_):
    path = safe_path(file_path, allowed_paths)
    if not path:
        return {"error": "Evidence not accessible"}
    headers, rows = _read_csv(path)
    if column not in headers:
        return {"error": f"Column '{column}' not found", "available": headers}

    def match(cell):
        num_cell, num_val = _to_number(cell), _to_number(value)
        if op in ("gt", "lt", "gte", "lte") and num_cell is not None and num_val is not None:
            return {"gt": num_cell > num_val, "lt": num_cell < num_val,
                    "gte": num_cell >= num_val, "lte": num_cell <= num_val}[op]
        if op == "eq":
            return str(cell).strip().lower() == str(value).strip().lower()
        if op == "ne":
            return str(cell).strip().lower() != str(value).strip().lower()
        if op == "contains":
            return str(value).strip().lower() in str(cell).strip().lower()
        return False

    hits = [r for r in rows if match(r.get(column, ""))]
    return {"column": column, "op": op, "value": value,
            "match_count": len(hits), "rows": hits[:limit]}


def group_and_aggregate(file_path, group_by, agg_column=None, agg="count",
                        allowed_paths=None, **_):
    path = safe_path(file_path, allowed_paths)
    if not path:
        return {"error": "Evidence not accessible"}
    headers, rows = _read_csv(path)
    if group_by not in headers:
        return {"error": f"Column '{group_by}' not found", "available": headers}
    buckets = defaultdict(list)
    for r in rows:
        buckets[r.get(group_by, "").strip()].append(r)

    results = []
    for key, group in buckets.items():
        if agg == "count" or not agg_column:
            val = len(group)
        else:
            nums = [x for x in (_to_number(r.get(agg_column, "")) for r in group) if x is not None]
            if not nums:
                val = 0
            else:
                val = {"sum": sum(nums), "mean": sum(nums) / len(nums),
                       "min": min(nums), "max": max(nums)}.get(agg, len(nums))
        results.append({"key": key, "value": round(val, 2)})
    results.sort(key=lambda x: x["value"], reverse=True)
    return {"group_by": group_by, "agg": agg, "agg_column": agg_column, "groups": results}


def top_n(file_path, column, n=5, by=None, agg="sum", allowed_paths=None, **_):
    path = safe_path(file_path, allowed_paths)
    if not path:
        return {"error": "Evidence not accessible"}
    if by:
        res = group_and_aggregate(file_path, column, by, agg, allowed_paths=allowed_paths)
        return {"column": column, "by": by, "agg": agg, "top": res.get("groups", [])[:n]}
    headers, rows = _read_csv(path)
    vc = Counter(r.get(column, "").strip() for r in rows if r.get(column, "").strip())
    return {"column": column, "top": [{"key": v, "value": c} for v, c in vc.most_common(n)]}


def compare_periods(file_path, date_column, value_column, period="month",
                    allowed_paths=None, **_):
    path = safe_path(file_path, allowed_paths)
    if not path:
        return {"error": "Evidence not accessible"}
    headers, rows = _read_csv(path)
    buckets = defaultdict(lambda: {"total": 0.0, "count": 0})
    for r in rows:
        d = _to_date(r.get(date_column, ""))
        if not d:
            continue
        key = d.strftime("%Y-%m") if period == "month" else d.strftime("%Y-%m-%d")
        amt = _to_number(r.get(value_column, "")) or 0
        buckets[key]["total"] += amt
        buckets[key]["count"] += 1
    series = [{"period": k, "total": round(v["total"], 2), "count": v["count"]}
              for k, v in sorted(buckets.items())]
    pct = None
    if len(series) >= 2 and series[-2]["total"]:
        pct = round((series[-1]["total"] - series[-2]["total"]) / series[-2]["total"] * 100, 1)
    return {"date_column": date_column, "value_column": value_column,
            "period": period, "series": series, "pct_change_last": pct}


def make_chart(chart_type, labels, values, title="", **_):
    """Return a validated chart spec (rendered by the report/workspace)."""
    chart_type = chart_type if chart_type in ("bar", "line", "pie") else "bar"
    labels = list(labels or [])[:24]
    values = [round(_to_number(v) or 0, 2) for v in (values or [])][:24]
    return {"type": chart_type, "title": title, "labels": labels, "values": values}


# ── Real evidence-derived helpers used by the deterministic pipeline ──
def build_timeline(file_path=None, events_description=None, allowed_paths=None, **_):
    """Extract a real, sorted chronology from a CSV's date column(s)."""
    events = []
    path = safe_path(file_path, allowed_paths) if file_path else None
    if path and path.lower().endswith(".csv"):
        headers, rows = _read_csv(path)
        date_cols = [h for h in headers if _infer_dtype([r.get(h, "") for r in rows]) == "date"]
        label_col = next((h for h in headers if _looks_like_id(h)), None)
        val_col = next((h for h, in [(h,) for h in headers]
                        if _infer_dtype([r.get(h, "") for r in rows]) == "number"), None)
        for dc in date_cols[:1]:
            for r in rows:
                d = _to_date(r.get(dc, ""))
                if not d:
                    continue
                bits = []
                if label_col and r.get(label_col):
                    bits.append(str(r.get(label_col)))
                if val_col and r.get(val_col):
                    bits.append(str(r.get(val_col)))
                events.append({"date": d.strftime("%Y-%m-%d"),
                               "label": " · ".join(bits) or os.path.basename(path)})
    elif events_description:
        for token in re.findall(r"\d{4}-\d{2}-\d{2}", events_description):
            events.append({"date": token, "label": "event"})
    events.sort(key=lambda e: e["date"])
    return {"events": events, "count": len(events)}


def map_relationships(file_path=None, entities_description=None, allowed_paths=None, **_):
    """Build a real node/edge graph from identifier-like columns of a CSV."""
    nodes, edges = {}, []
    path = safe_path(file_path, allowed_paths) if file_path else None

    def kind_of(col):
        c = col.lower()
        if "vendor" in c or "supplier" in c or "company" in c or "merchant" in c:
            return "Vendor"
        if "account" in c or "acct" in c:
            return "Account"
        if "invoice" in c or c.startswith("inv"):
            return "Invoice"
        if "email" in c or "mail" in c:
            return "Email"
        if "person" in c or "name" in c or "witness" in c or "employee" in c:
            return "Person"
        if "txn" in c or "transaction" in c or "payment" in c:
            return "Transaction"
        return "Entity"

    if path and path.lower().endswith(".csv"):
        headers, rows = _read_csv(path)
        ent_cols = [h for h in headers if _looks_like_id(h) or kind_of(h) != "Entity"][:4]
        for r in rows:
            present = []
            for c in ent_cols:
                v = r.get(c, "").strip()
                if not v:
                    continue
                nid = f"{kind_of(c)}:{v}"
                nodes[nid] = {"id": nid, "label": v, "type": kind_of(c)}
                present.append(nid)
            for i in range(len(present)):
                for j in range(i + 1, len(present)):
                    edges.append({"source": present[i], "target": present[j]})
    # de-dupe edges
    seen, uniq = set(), []
    for e in edges:
        k = tuple(sorted((e["source"], e["target"])))
        if k not in seen:
            seen.add(k)
            uniq.append(e)
    return {"nodes": list(nodes.values()), "edges": uniq[:60]}


def consult_previous_cases(query, investigation_id=None, user_id=None, **_):
    """Search the Memory table for related past investigations (real overlap)."""
    try:
        from backend.models import Memory
        q = Memory.query
        if user_id:
            q = q.filter(Memory.user_id == user_id)
        memories = q.all()
    except Exception:
        memories = []
    terms = set(re.findall(r"[a-zA-Z]{4,}", (query or "").lower()))
    matches = []
    for m in memories:
        text = f"{m.key} {m.value}".lower()
        mterms = set(re.findall(r"[a-zA-Z]{4,}", text))
        if not mterms:
            continue
        overlap = len(terms & mterms) / max(1, len(terms | mterms))
        if overlap > 0:
            matches.append({"key": m.key, "value": m.value,
                            "similarity": round(overlap * 100)})
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return {"query": query, "matches": matches[:5], "count": len(matches)}


# ── Backward-compatible wrappers (now REAL, no more "Mock ...") ───────
def analyze_csv(file_path, query=None, allowed_paths=None, **_):
    return profile_dataset(file_path, allowed_paths=allowed_paths)


def analyze_document(file_path, query=None, allowed_paths=None, **_):
    path = safe_path(file_path, allowed_paths)
    if not path:
        return {"error": "Evidence not accessible"}
    text = ""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8", errors="ignore")
    except Exception as e:
        return {"error": str(e)}
    words = re.findall(r"[a-zA-Z']+", text)
    keywords = [w for w, _ in Counter(w.lower() for w in words if len(w) > 4).most_common(8)]
    return {"file": os.path.basename(path), "char_count": len(text),
            "snippet": text[:400].strip(), "keywords": keywords}


def analyze_image(file_path, query=None, allowed_paths=None, **_):
    path = safe_path(file_path, allowed_paths)
    if not path:
        return {"error": "Evidence not accessible"}
    return {"file": os.path.basename(path), "type": "image",
            "size_bytes": os.path.getsize(path),
            "note": "Photographic evidence logged. Attach a vision model for pixel-level analysis."}


def search_evidence(query, investigation_id=None, **_):
    try:
        from backend.models import Evidence
        items = Evidence.query.filter_by(investigation_id=investigation_id).all()
    except Exception:
        items = []
    q = (query or "").lower()
    hits = [{"filename": e.filename, "file_type": e.file_type}
            for e in items if q in (e.filename or "").lower() or not q]
    return {"query": query, "matches": hits, "count": len(hits)}


def calculate_statistics(data_description=None, operation="sum", **_):
    nums = [float(x.replace(",", "")) for x in re.findall(r"-?[\d,]+\.?\d*", data_description or "")]
    if not nums:
        return {"operation": operation, "result": None, "note": "no numeric values found"}
    result = {"sum": sum(nums), "mean": sum(nums) / len(nums),
              "min": min(nums), "max": max(nums), "count": len(nums)}.get(operation, sum(nums))
    return {"operation": operation, "result": round(result, 2), "n": len(nums)}

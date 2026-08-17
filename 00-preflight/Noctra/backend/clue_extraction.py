"""Candidate-clue extraction (NOCTRA Phase 2).

Deterministic, pure-stdlib heuristics that turn a piece of evidence into a
handful of *candidate* clues. Nothing here confirms anything — the investigator
decides. Works fully in demo mode (no API key). When an OpenAI key is present
the caller may enrich these, but the deterministic path is always the fallback.
"""
import os
import re

AMOUNT_RE = re.compile(r'\$?\s?(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d{4,}(?:\.\d+)?)')
ENTITY_RE = re.compile(r'\b([A-Z][a-z]{2,}(?:\s+(?:[A-Z][a-z]{2,}|Holdings|Group|LLC|Inc|Ltd|Partners|Procurement|Capital|Systems))+)\b')
URGENT = ('urgent', 'immediately', 'asap', 'expedite', 'rush', 'right away', 'time-sensitive', 'as soon as possible')
OFFSHORE = ('offshore', 'overseas', 'wire transfer', 'holding company', 'shell', 'foreign account')

UNIQUE_ID_TOKENS = ('invoice', 'inv', 'receipt', 'rcp', 'claim', 'clm', 'txn', 'transaction', 'order', 'ref')
AMOUNT_TOKENS = ('amount', 'total', 'value', 'transfer', 'payment', 'sum', 'debit', 'credit', 'paid')
ENTITY_TOKENS = ('vendor', 'entity', 'payee', 'name', 'company', 'organization', 'account', 'supplier', 'counterparty', 'merchant')
DATE_TOKENS = ('date', 'created', 'onboard', 'since', 'timestamp', 'time', 'opened', 'registered')


def _num(v):
    try:
        return float(str(v).replace(',', '').replace('$', '').strip())
    except Exception:
        return None


def _find_col(headers, tokens):
    for i, h in enumerate(headers):
        hl = (h or '').lower()
        if any(t in hl for t in tokens):
            return i
    return None


def _csv_clues(filename, path):
    from backend import tools as T
    resolved = T.safe_path(os.path.basename(path), [path])
    if not resolved:
        return []
    headers, rows = T._read_csv(resolved, limit=2000)
    if not headers or not rows:
        return []
    out = []

    amt_i = _find_col(headers, AMOUNT_TOKENS)
    ent_i = _find_col(headers, ENTITY_TOKENS)
    date_i = _find_col(headers, DATE_TOKENS)

    # 1) Unusually large transaction (max amount)
    if amt_i is not None:
        best, best_v = None, -1
        for r in rows:
            v = _num(r.get(headers[amt_i]))
            if v is not None and v > best_v:
                best_v, best = v, r
        if best is not None and best_v > 0:
            ent = (best.get(headers[ent_i]) if ent_i is not None else '') or 'an unnamed party'
            when = (best.get(headers[date_i]) if date_i is not None else '') or ''
            out.append({
                'title': 'Large transfer',
                'description': f"${best_v:,.0f} to {ent}" + (f" on {when}" if when else ''),
                'signal': 'Unusually large transaction',
                'entity': str(ent),
                'source_location': (f"row: {when}" if when else 'largest row'),
                'clue_type': 'fact',
                'confidence': 82,
            })

    # 2) Duplicate identifier that should be unique
    prof = T.profile_dataset(os.path.basename(path), allowed_paths=[path])
    for col, reps in (prof.get('duplicate_keys') or {}).items():
        if reps:
            v = reps[0]['value']; n = reps[0]['count']
            out.append({
                'title': f'Duplicate {col}',
                'description': f"{v} appears {n}× — an identifier that should be unique.",
                'signal': 'Repeated identifier / possible duplicate record',
                'entity': str(v),
                'source_location': f"column: {col}",
                'clue_type': 'fact',
                'confidence': 86,
            })
            break

    # 3) Recently created / new counterparty (if an onboarding-style date exists)
    created_i = _find_col(headers, ('created', 'onboard', 'since', 'opened', 'registered'))
    if created_i is not None and ent_i is not None and len(rows) > 1:
        def keyf(r):
            return str(r.get(headers[created_i]) or '')
        newest = sorted(rows, key=keyf)[-1]
        ent = newest.get(headers[ent_i]) or 'a vendor'
        out.append({
            'title': 'Recently created vendor',
            'description': f"{ent} was created on {newest.get(headers[created_i])} — shortly before activity in this ledger.",
            'signal': 'New vendor created just before payment',
            'entity': str(ent),
            'source_location': f"created: {newest.get(headers[created_i])}",
            'clue_type': 'pattern',
            'confidence': 71,
        })

    return out[:3]


def _text_clues(filename, path):
    from backend import tools as T
    resolved = T.safe_path(os.path.basename(path), [path])
    text = ''
    if resolved and os.path.exists(resolved):
        try:
            with open(resolved, 'rb') as fh:
                text = fh.read(8000).decode('utf-8', errors='ignore')
        except Exception:
            text = ''
    if not text.strip():
        return []
    low = text.lower()
    out = []
    entities = ENTITY_RE.findall(text)
    primary_entity = entities[0] if entities else ''

    m = AMOUNT_RE.search(text)
    if m:
        val = _num(m.group(1))
        if val:
            out.append({
                'title': 'Monetary figure referenced',
                'description': f"A figure of ${val:,.0f} is named in {filename}.",
                'signal': 'Large monetary figure in correspondence',
                'entity': primary_entity,
                'source_location': 'body text',
                'clue_type': 'fact',
                'confidence': 70,
            })

    if any(w in low for w in URGENT):
        out.append({
            'title': 'Urgent approval request',
            'description': f"{filename} presses for an unusually fast approval.",
            'signal': 'Unusual urgency around approval',
            'entity': primary_entity,
            'source_location': 'body text',
            'clue_type': 'fact',
            'confidence': 75,
        })

    if any(w in low for w in OFFSHORE):
        out.append({
            'title': 'Offshore / holding reference',
            'description': f"{filename} references an offshore or holding arrangement.",
            'signal': 'Funds routed via holding/offshore entity',
            'entity': primary_entity,
            'source_location': 'body text',
            'clue_type': 'pattern',
            'confidence': 68,
        })

    if primary_entity and len(out) < 3:
        out.append({
            'title': f'Counterparty: {primary_entity}',
            'description': f"{primary_entity} is named in {filename}.",
            'signal': 'Named counterparty of interest',
            'entity': primary_entity,
            'source_location': 'body text',
            'clue_type': 'fact',
            'confidence': 60,
        })

    return out[:3]


def _pdf_clues(filename, path):
    stem = re.sub(r'\.[a-z]+$', '', filename, flags=re.I)
    ident = ''
    m = re.search(r'[A-Z]{2,}[- ]?\d{2,}', filename)
    if m:
        ident = m.group(0)
    return [{
        'title': f'Document: {stem}',
        'description': f"{filename} is on file. Cross-reference its contents against the ledger and correspondence.",
        'signal': 'Referenced document / invoice',
        'entity': ident or stem,
        'source_location': 'document',
        'clue_type': 'fact',
        'confidence': 58,
    }]


def _image_clues(filename, path):
    return [{
        'title': f'Photographic exhibit: {filename}',
        'description': 'A visual exhibit requiring inspection.',
        'signal': 'Image evidence',
        'entity': '',
        'source_location': 'image',
        'clue_type': 'fact',
        'confidence': 42,
    }]


def extract_candidate_clues(filename, file_type, file_path):
    """Return a list of candidate-clue dicts for one evidence item."""
    ft = (file_type or '').lower()
    try:
        if ft == 'csv':
            return _csv_clues(filename, file_path)
        if ft in ('image',):
            return _image_clues(filename, file_path)
        if ft == 'pdf':
            return _pdf_clues(filename, file_path)
        return _text_clues(filename, file_path)
    except Exception:
        return []

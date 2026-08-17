import os
import json
import re
from flask import Flask, jsonify, request, render_template, Response, session
from backend.config import Config
from backend.database import init_db, db_session
from backend.auth import auth_bp
from backend.models import Investigation, Evidence, User
from backend.planner import create_investigation_plan
from backend.agent import InvestigationAgent
from backend.memory import store_memory, get_all_memories
from datetime import datetime
import uuid

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL

app.register_blueprint(auth_bp)

@app.before_request
def setup():
    if not getattr(app, '_database_initialized', False):
        init_db()
        app._database_initialized = True

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# ── Page Routes ──────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/access')
def access():
    return render_template('access.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/hub')
def hub():
    return render_template('hub.html')

@app.route('/investigation/new')
def new_investigation_page():
    return render_template('create_investigation.html')

@app.route('/evidence-board')
def evidence_board_page():
    """Cross-case Evidence Board: pick any case from the bureau and see the
    evidence already linked to it, without leaving this page. Opening a
    case here never starts a new investigation — 'New Case' is the only
    place that begins one."""
    return render_template('evidence_board.html')

@app.route('/investigation/<int:inv_id>/evidence')
def evidence_intake_page(inv_id):
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return render_template('archive.html'), 404
    return render_template('evidence_intake.html', investigation=inv)

@app.route('/investigation/<int:inv_id>')
def workspace_page(inv_id):
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return render_template('archive.html'), 404
    return render_template('workspace.html', investigation=inv)

@app.route('/investigation/<int:inv_id>/report')
def report_page(inv_id):
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return render_template('archive.html'), 404
    return render_template('report.html', investigation=inv)

@app.route('/archive')
def archive_page():
    return render_template('archive.html')

@app.route('/memory')
def memory_page():
    return render_template('memory.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

# ── API Routes ───────────────────────────────────────────────────────

@app.route('/api/investigations', methods=['POST'])
def create_investigation():
    data = request.json or {}
    user_id = session.get('user_id')
    inv = Investigation(
        user_id=int(user_id) if user_id else None,
        case_number=f"NOC-{datetime.now().year}-{str(uuid.uuid4())[:4].upper()}",
        case_name=data.get('case_name', 'Untitled Case'),
        description=data.get('description', ''),
        status='active'
    )
    db_session.add(inv)
    db_session.commit()
    return jsonify({"id": inv.id, "case_number": inv.case_number, "case_name": inv.case_name}), 201

@app.route('/api/investigations', methods=['GET'])
def list_investigations():
    include_deleted = request.args.get('include_deleted') == '1'
    q = Investigation.query
    if not include_deleted:
        q = q.filter(Investigation.status != 'deleted')
    invs = q.order_by(Investigation.created_at.desc()).all()
    return jsonify([{
        "id": i.id,
        "case_number": i.case_number,
        "case_name": i.case_name,
        "description": i.description,
        "status": i.status,
        "created_at": i.created_at.isoformat() if i.created_at else None
    } for i in invs])

@app.route('/api/investigations/<int:inv_id>', methods=['GET'])
def get_investigation(inv_id):
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return jsonify(error="Case not found"), 404
    return jsonify({
        "id": inv.id,
        "case_number": inv.case_number,
        "case_name": inv.case_name,
        "description": inv.description,
        "status": inv.status
    })

@app.route('/api/investigations/<int:inv_id>/evidence', methods=['POST'])
def upload_evidence(inv_id):
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return jsonify(error="Case not found"), 404
    if 'file' not in request.files:
        return jsonify(error="No evidence file provided"), 400
    f = request.files['file']
    filename = f"{uuid.uuid4().hex[:8]}_{f.filename}"
    filepath = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    f.save(filepath)
    ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else 'unknown'
    file_type_map = {'csv': 'csv', 'pdf': 'pdf', 'png': 'image', 'jpg': 'image', 'jpeg': 'image', 'mp3': 'audio', 'wav': 'audio'}
    evidence = Evidence(
        investigation_id=inv_id,
        filename=f.filename,
        file_type=file_type_map.get(ext, 'notes'),
        file_path=filepath
    )
    db_session.add(evidence)
    db_session.commit()
    return jsonify({"success": True, "evidence_id": evidence.id, "filename": f.filename}), 201

@app.route('/api/investigations/<int:inv_id>/evidence', methods=['GET'])
def list_evidence(inv_id):
    from backend.models import Clue
    items = Evidence.query.filter_by(investigation_id=inv_id).all()
    out = []
    for e in items:
        clues = Clue.query.filter_by(evidence_id=e.id).order_by(Clue.id).all()
        out.append({
            "id": e.id,
            "filename": e.filename,
            "file_type": e.file_type,
            "analyzed": bool(e.analysis_result),
            "candidate_clues": [_clue_json(c) for c in clues],
            "uploaded_at": e.uploaded_at.isoformat() if e.uploaded_at else None
        })
    return jsonify(out)

def _clue_json(c):
    return {
        "id": c.id,
        "clue_number": f"#{c.id:03d}",
        "title": c.title,
        "description": c.description,
        "signal": c.signal,
        "entity": c.entity,
        "source": c.source,
        "source_location": c.source_location,
        "confidence": c.confidence,
        "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }

@app.route('/api/investigations/<int:inv_id>/evidence/<int:eid>/analyze', methods=['POST'])
def analyze_evidence(inv_id, eid):
    """Phase 1/2: run deterministic candidate-clue extraction over one piece
    of evidence and persist each finding as a Clue row with status
    'candidate'. Nothing here confirms a clue — that's the investigator's
    decision via /api/clues/<id>/decision."""
    from backend.models import Clue
    ev = db_session.get(Evidence, eid)
    if not ev or ev.investigation_id != inv_id:
        return jsonify(error="Evidence not found"), 404

    # Re-analyzing replaces only untouched candidates; confirmed/rejected
    # clues the investigator already decided on are left alone.
    Clue.query.filter_by(evidence_id=eid, status='candidate').delete()
    db_session.commit()

    from backend.clue_extraction import extract_candidate_clues
    found = extract_candidate_clues(ev.filename, ev.file_type, ev.file_path)
    created = []
    for f in found:
        c = Clue(
            investigation_id=inv_id,
            evidence_id=eid,
            title=f.get('title'),
            description=f.get('description'),
            signal=f.get('signal'),
            entity=f.get('entity'),
            source=ev.filename,
            confidence=f.get('confidence', 50),
            status='candidate',
        )
        db_session.add(c)
        created.append(c)
    ev.analysis_result = 'analyzed'
    db_session.commit()
    return jsonify({
        "evidence_id": ev.id,
        "filename": ev.filename,
        "candidate_clues": [_clue_json(c) for c in created]
    })

@app.route('/api/investigations/<int:inv_id>/clues', methods=['GET'])
def list_clues(inv_id):
    from backend.models import Clue
    status = request.args.get('status')
    q = Clue.query.filter_by(investigation_id=inv_id)
    if status:
        q = q.filter_by(status=status)
    clues = q.order_by(Clue.id).all()
    return jsonify([_clue_json(c) for c in clues])

@app.route('/api/clues/<int:cid>/decision', methods=['POST'])
def clue_decision(cid):
    """The investigator's call: MARK AS CLUE (confirm) or NOT RELEVANT
    (reject). This is the one place a candidate becomes — or doesn't
    become — a real investigation clue."""
    from backend.models import Clue
    c = db_session.get(Clue, cid)
    if not c:
        return jsonify(error="Clue not found"), 404
    action = (request.json or {}).get('action')
    if action == 'confirm':
        c.status = 'confirmed'
    elif action == 'reject':
        c.status = 'rejected'
    else:
        return jsonify(error="Unknown action"), 400
    db_session.commit()
    return jsonify(_clue_json(c))

@app.route('/api/investigations/<int:inv_id>/logs', methods=['GET'])
def list_logs(inv_id):
    from backend.models import InvestigationLog
    logs = InvestigationLog.query.filter_by(investigation_id=inv_id).order_by(InvestigationLog.timestamp).all()
    return jsonify([{
        "step_type": l.step_type,
        "content": l.content,
        "timestamp": l.timestamp.isoformat() if l.timestamp else None
    } for l in logs])

@app.route('/api/investigations/<int:inv_id>', methods=['DELETE'])
def delete_investigation(inv_id):
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return jsonify(error="Case not found"), 404
    inv.status = 'deleted'
    db_session.commit()
    return jsonify({"success": True}), 200

@app.route('/api/investigations/<int:inv_id>/restore', methods=['POST'])
def restore_investigation(inv_id):
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return jsonify(error="Case not found"), 404
    inv.status = 'active'
    db_session.commit()
    return jsonify({"success": True}), 200

@app.route('/api/investigations/<int:inv_id>/investigate', methods=['POST'])
def start_investigation(inv_id):
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return jsonify(error="Case not found"), 404
    evidence_list = [e.filename for e in Evidence.query.filter_by(investigation_id=inv_id).all()]
    plan = create_investigation_plan(inv.case_name, inv.description, evidence_list)
    agent = InvestigationAgent(inv_id, Config.OPENAI_API_KEY)
    user_id = session.get('user_id')
    case_name = inv.case_name

    def generate():
        completed_steps = []
        for step in agent.run_investigation(plan):
            completed_steps.append(step['step'])
            yield f"data: {json.dumps(step)}\n\n"
        if user_id and completed_steps:
            store_memory(
                int(user_id),
                key=f"Case Closed: {case_name}",
                value=f"Investigated via: {', '.join(completed_steps)}.",
                investigation_id=inv_id
            )
        # a completed investigation moves the case into the Solved drawer
        try:
            fresh = db_session.get(Investigation, inv_id)
            if fresh and completed_steps and fresh.status == 'active':
                fresh.status = 'solved'
                db_session.commit()
        except Exception:
            pass
        yield "data: {\"type\": \"complete\"}\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

@app.route('/api/investigations/<int:inv_id>/report', methods=['GET'])
def get_report(inv_id):
    from backend.evaluate import evaluate_investigation
    return jsonify(evaluate_investigation(inv_id))

@app.route('/api/memory', methods=['GET'])
def get_memories():
    from backend.models import Memory
    user_id = session.get('user_id')
    if user_id:
        memories = (Memory.query
                    .filter((Memory.user_id == int(user_id)) | (Memory.user_id.is_(None)))
                    .order_by(Memory.created_at.desc()).all())
    else:
        # shared / featured-case discoveries are visible without signing in
        memories = (Memory.query.filter(Memory.user_id.is_(None))
                    .order_by(Memory.created_at.desc()).all())
    return jsonify([{
        "id": m.id,
        "key": m.key,
        "value": m.value,
        "investigation_id": m.investigation_id,
        "created_at": m.created_at.isoformat() if m.created_at else None
    } for m in memories])

@app.route('/api/memory', methods=['POST'])
def store_mem():
    data = request.json or {}
    user_id = session.get('user_id')
    if user_id:
        store_memory(int(user_id), data.get('key', ''), data.get('value', ''))
    return jsonify({"success": True}), 201

# ── Feature APIs (evidence preview, voice, notebook, memory, challenge) ──

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    from flask import send_from_directory
    safe_dir = os.path.abspath('uploads')
    return send_from_directory(safe_dir, filename)

@app.route('/api/investigations/<int:inv_id>/evidence/<int:eid>/preview', methods=['GET'])
def evidence_preview(inv_id, eid):
    ev = db_session.get(Evidence, eid)
    if not ev or ev.investigation_id != inv_id:
        return jsonify(error="Evidence not found"), 404
    from backend import tools as T
    fname = os.path.basename(ev.file_path or ev.filename)
    url = f"/uploads/{fname}"
    ftype = (ev.file_type or 'notes').lower()
    resolved = T.safe_path(fname, [ev.file_path] if ev.file_path else None)

    if ftype == 'csv' and resolved:
        headers, rows = T._read_csv(resolved, limit=12)
        prof = T.profile_dataset(fname, allowed_paths=[ev.file_path])
        dup_vals = []
        for reps in (prof.get('duplicate_keys') or {}).values():
            dup_vals += [r['value'] for r in reps]
        return jsonify(type='csv', filename=ev.filename, columns=headers,
                       record_count=prof.get('record_count', len(rows)),
                       duplicates=dup_vals, rows=rows[:12], url=url)
    if ftype == 'image':
        return jsonify(type='image', filename=ev.filename, url=url)
    if ftype == 'pdf':
        return jsonify(type='pdf', filename=ev.filename, url=url)
    if ftype == 'audio':
        peaks = []
        if resolved and os.path.exists(resolved):
            with open(resolved, 'rb') as fh:
                b = fh.read(4000)
            step = max(1, len(b) // 60) if b else 1
            peaks = [b[i] / 255 for i in range(0, len(b), step)][:60] or [0.2] * 40
        return jsonify(type='audio', filename=ev.filename, url=url, peaks=peaks)
    # notes / txt / unknown → text preview
    text = ''
    if resolved and os.path.exists(resolved):
        try:
            with open(resolved, 'rb') as fh:
                text = fh.read(4000).decode('utf-8', errors='ignore')
        except Exception:
            text = ''
    return jsonify(type='text', filename=ev.filename, text=text, url=url)

@app.route('/api/tts', methods=['POST'])
def tts():
    """OpenAI text-to-speech. Returns audio when a key is set; 204 otherwise so
    the frontend falls back to the browser's speech synthesis."""
    data = request.json or {}
    text = (data.get('text') or '').strip()[:600]
    if not text or not Config.OPENAI_API_KEY:
        return ('', 204)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        voice = data.get('voice', 'onyx')
        model = os.environ.get('OPENAI_TTS_MODEL', 'tts-1')
        speech = client.audio.speech.create(model=model, voice=voice, input=text)
        audio = speech.read() if hasattr(speech, 'read') else speech.content
        return Response(audio, mimetype='audio/mpeg')
    except Exception:
        return ('', 204)

def _note_json(n):
    return {
        "id": n.id, "body": n.body,
        "pinned": bool(n.pinned), "x": n.pin_x, "y": n.pin_y,
        "created_at": n.created_at.isoformat() if n.created_at else None,
        "updated_at": n.updated_at.isoformat() if n.updated_at else None,
    }

@app.route('/api/investigations/<int:inv_id>/notes', methods=['GET', 'POST'])
def notes(inv_id):
    from backend.models import Note
    if request.method == 'POST':
        body = (request.json or {}).get('body', '').strip()
        if not body:
            return jsonify(error="Empty note"), 400
        n = Note(investigation_id=inv_id, body=body)
        db_session.add(n)
        db_session.commit()
        return jsonify(_note_json(n)), 201
    items = Note.query.filter_by(investigation_id=inv_id).order_by(Note.created_at.desc()).all()
    return jsonify([_note_json(n) for n in items])

@app.route('/api/notes/<int:nid>', methods=['PUT', 'DELETE'])
def note_detail(nid):
    from backend.models import Note
    n = db_session.get(Note, nid)
    if not n:
        return jsonify(error="Note not found"), 404
    if request.method == 'DELETE':
        db_session.delete(n)
        db_session.commit()
        return jsonify(success=True)
    body = (request.json or {}).get('body', '').strip()
    if not body:
        return jsonify(error="Empty note"), 400
    n.body = body
    db_session.commit()
    return jsonify(_note_json(n))

@app.route('/api/notes/<int:nid>/pin', methods=['POST'])
def note_pin(nid):
    """Extract a note onto the board as a sticky note (pinned=true, with an
    x/y position), or send it back to the notebook (pinned=false)."""
    from backend.models import Note
    n = db_session.get(Note, nid)
    if not n:
        return jsonify(error="Note not found"), 404
    d = request.json or {}
    pinned = d.get('pinned', True)
    n.pinned = 1 if pinned else 0
    if pinned:
        if 'x' in d: n.pin_x = int(d['x'])
        if 'y' in d: n.pin_y = int(d['y'])
    db_session.commit()
    return jsonify(_note_json(n))

@app.route('/api/notes/search', methods=['GET'])
def notes_search():
    from backend.models import Note
    q = (request.args.get('q') or '').strip().lower()
    items = Note.query.order_by(Note.created_at.desc()).all()
    out = [{"id": n.id, "investigation_id": n.investigation_id, "body": n.body}
           for n in items if not q or q in (n.body or '').lower()]
    return jsonify(out)

@app.route('/api/investigations/<int:inv_id>/challenge', methods=['POST'])
def challenge(inv_id):
    from backend.evaluate import challenge_investigation
    return jsonify(challenge_investigation(inv_id))

@app.route('/api/investigations/<int:inv_id>/status', methods=['POST'])
def set_status(inv_id):
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return jsonify(error="Case not found"), 404
    new_status = (request.json or {}).get('status', '')
    if new_status in ('active', 'solved', 'closed'):
        inv.status = new_status
        db_session.commit()
    return jsonify(success=True, status=inv.status)

# ── Interactive investigation (board · connections · patterns) ───────

def _compute_state(inv_id):
    from backend.models import Clue, Relationship
    confirmed = Clue.query.filter_by(investigation_id=inv_id, status='confirmed').all()
    placed = [c for c in confirmed if c.placed]
    rels = Relationship.query.filter_by(investigation_id=inv_id, status='supported').all()
    signals = ' '.join(((c.signal or '') + ' ' + (c.title or '')) for c in confirmed).lower()
    has_transfer = any(('transfer' in (c.title or '').lower())
                       or ('large' in (c.signal or '').lower())
                       or ('transaction' in (c.signal or '').lower()) for c in confirmed)
    has_approval = any(w in signals for w in ('approval', 'approve', 'urgent'))
    missing = []
    if has_transfer and confirmed and not has_approval:
        missing.append('An approval record linking the vendor to the procurement decision')
    if len(confirmed) >= 2 and not rels:
        missing.append('At least one supported connection between clues')
    conf = 18 + len(confirmed) * 8 + len(rels) * 13
    conf = max(5, min(95, conf - (10 if missing else 0)))
    ready = conf >= 70 and len(rels) >= 1 and not missing
    return {
        'confidence': conf, 'ready': ready, 'missing': missing,
        'counts': {'confirmed': len(confirmed), 'placed': len(placed),
                   'relationships': len(rels)},
    }

@app.route('/api/investigations/<int:inv_id>/board', methods=['GET'])
def get_board(inv_id):
    from backend.models import Clue, Relationship, Investigation
    confirmed = Clue.query.filter_by(investigation_id=inv_id, status='confirmed').order_by(Clue.id).all()
    rels = Relationship.query.filter_by(investigation_id=inv_id).all()
    inv = db_session.get(Investigation, inv_id)
    return jsonify({
        'clues': [_clue_json(c) | {'placed': bool(c.placed), 'x': c.board_x, 'y': c.board_y,
                                   'origin': c.origin, 'clue_type': c.clue_type} for c in confirmed],
        'relationships': [{
            'id': r.id, 'source': r.source_clue_id, 'target': r.target_clue_id,
            'type': r.relationship_type, 'status': r.status,
            'basis': r.evidence_basis, 'confidence': r.confidence} for r in rels],
        'state': _compute_state(inv_id),
        'case_name': inv.case_name if inv else '',
    })

@app.route('/api/clues/<int:cid>/place', methods=['POST'])
def place_clue(cid):
    from backend.models import Clue
    c = db_session.get(Clue, cid)
    if not c:
        return jsonify(error="Clue not found"), 404
    d = request.json or {}
    if 'x' in d: c.board_x = int(d['x'])
    if 'y' in d: c.board_y = int(d['y'])
    if 'placed' in d: c.placed = 1 if d['placed'] else 0
    db_session.commit()
    return jsonify(_clue_json(c) | {'placed': bool(c.placed), 'x': c.board_x, 'y': c.board_y})

def _evaluate_connection(a, b):
    ea = (a.entity or '').strip().lower()
    eb = (b.entity or '').strip().lower()
    def blob(c): return ' '.join(filter(None, [c.title, c.description, c.signal, c.entity])).lower()
    if ea and eb and ea == eb:
        return 'supported', 'references the same entity', f"Both clues reference {a.entity}.", 82
    if a.source and b.source and a.source == b.source:
        return 'supported', 'drawn from the same exhibit', f"Both clues come from {a.source}.", 70
    if ea and ea in blob(b):
        return 'supported', 'entity referenced', f"{a.entity} is referenced by the connected clue.", 68
    if eb and eb in blob(a):
        return 'supported', 'entity referenced', f"{b.entity} is referenced by the connected clue.", 68
    return ('rejected', None,
            "These pieces of evidence do not currently establish a relationship.", 0)

@app.route('/api/investigations/<int:inv_id>/connect', methods=['POST'])
def connect_clues(inv_id):
    from backend.models import Clue, Relationship
    d = request.json or {}
    a = db_session.get(Clue, int(d.get('source', 0)))
    b = db_session.get(Clue, int(d.get('target', 0)))
    if not a or not b or a.id == b.id:
        return jsonify(error="Two distinct clues required"), 400
    existing = Relationship.query.filter(
        Relationship.investigation_id == inv_id,
        ((Relationship.source_clue_id == a.id) & (Relationship.target_clue_id == b.id)) |
        ((Relationship.source_clue_id == b.id) & (Relationship.target_clue_id == a.id))).first()
    if existing:
        return jsonify(status=existing.status, id=existing.id,
                       type=existing.relationship_type, basis=existing.evidence_basis,
                       duplicate=True, state=_compute_state(inv_id))
    status, rtype, basis, conf = _evaluate_connection(a, b)
    if status == 'rejected':
        return jsonify(status='rejected', basis=basis, state=_compute_state(inv_id))
    r = Relationship(investigation_id=inv_id, source_clue_id=a.id, target_clue_id=b.id,
                     relationship_type=rtype, status='supported', evidence_basis=basis,
                     confidence=conf)
    db_session.add(r); db_session.commit()
    return jsonify(status='supported', id=r.id, type=rtype, basis=basis,
                   confidence=conf, state=_compute_state(inv_id))

@app.route('/api/relationships/<int:rid>', methods=['DELETE'])
def delete_relationship(rid):
    from backend.models import Relationship
    r = db_session.get(Relationship, rid)
    if r:
        inv = r.investigation_id
        db_session.delete(r); db_session.commit()
        return jsonify(success=True, state=_compute_state(inv))
    return jsonify(success=False), 404

@app.route('/api/investigations/<int:inv_id>/missing', methods=['GET'])
def missing_links(inv_id):
    state = _compute_state(inv_id)
    if not state['missing']:
        return jsonify(missing=False, state=state)
    first = state['missing'][0]
    return jsonify(missing=True, title="Something doesn't add up",
                   message=first, items=state['missing'], state=state)

@app.route('/api/investigations/<int:inv_id>/patterns', methods=['GET'])
def detect_patterns(inv_id):
    """Compare confirmed clues against prior cases + shared memory patterns."""
    from backend.models import Clue, Memory, Investigation
    confirmed = Clue.query.filter_by(investigation_id=inv_id, status='confirmed').all()
    if not confirmed:
        return jsonify([])

    def toks(s):
        return set(re.findall(r'[a-z]{4,}', (s or '').lower()))
    results = []
    # against other investigations' confirmed clues
    others = (db_session.query(Clue, Investigation)
              .join(Investigation, Clue.investigation_id == Investigation.id)
              .filter(Clue.investigation_id != inv_id, Clue.status == 'confirmed').all())
    for c in confirmed:
        ce = (c.entity or '').lower()
        cblob = toks(f"{c.title} {c.signal} {c.entity}")
        for oc, oinv in others:
            oe = (oc.entity or '').lower()
            overlap = cblob & toks(f"{oc.title} {oc.signal} {oc.entity}")
            sim = 0
            if ce and oe and ce == oe:
                sim = 88
            elif overlap:
                sim = min(85, 45 + 12 * len(overlap))
            if sim >= 55:
                results.append({'current_clue': c.title, 'current_entity': c.entity,
                                'previous_case': oinv.case_number,
                                'previous_pattern': oc.signal or oc.title,
                                'similarity': sim,
                                'suggested': {'title': f"Pattern match: {oc.title}",
                                              'description': f"Resembles {oinv.case_number}: {oc.signal or oc.title}.",
                                              'entity': c.entity, 'confidence': sim}})
    # against shared memory patterns
    mems = Memory.query.filter(Memory.user_id.is_(None)).all()
    for c in confirmed:
        cblob = toks(f"{c.title} {c.signal} {c.entity}")
        for m in mems:
            overlap = cblob & toks(f"{m.key} {m.value}")
            if len(overlap) >= 2:
                sim = min(84, 50 + 10 * len(overlap))
                results.append({'current_clue': c.title, 'current_entity': c.entity,
                                'previous_case': (m.key or 'Prior pattern'),
                                'previous_pattern': m.value,
                                'similarity': sim,
                                'suggested': {'title': f"Known pattern: {m.key}",
                                              'description': m.value, 'entity': c.entity,
                                              'confidence': sim}})
    # dedupe by (current_clue, previous_case), keep highest sim, top 4
    seen = {}
    for r in sorted(results, key=lambda x: -x['similarity']):
        k = (r['current_clue'], r['previous_case'])
        if k not in seen:
            seen[k] = r
    return jsonify(list(seen.values())[:4])

@app.route('/api/investigations/<int:inv_id>/patterns/adopt', methods=['POST'])
def adopt_pattern(inv_id):
    from backend.models import Clue
    d = request.json or {}
    c = Clue(investigation_id=inv_id, evidence_id=None,
             title=d.get('title', 'Adopted pattern'),
             description=d.get('description', ''),
             signal='Pattern from previous case', entity=d.get('entity', ''),
             source=d.get('previous_case', 'Previous case'),
             clue_type='pattern', confidence=int(d.get('confidence', 70)),
             status='confirmed', placed=0, origin='previous_case')
    db_session.add(c); db_session.commit()
    return jsonify(_clue_json(c) | {'origin': c.origin})

@app.route('/api/investigations/<int:inv_id>/confidence', methods=['GET'])
def get_confidence(inv_id):
    return jsonify(_compute_state(inv_id))

@app.route('/api/investigations/<int:inv_id>/case-report', methods=['GET'])
def case_report(inv_id):
    from backend.models import Clue, Relationship, Evidence, Investigation, InvestigationLog
    inv = db_session.get(Investigation, inv_id)
    confirmed = Clue.query.filter_by(investigation_id=inv_id, status='confirmed').order_by(Clue.confidence.desc()).all()
    rejected = Clue.query.filter_by(investigation_id=inv_id, status='rejected').all()
    rels = Relationship.query.filter_by(investigation_id=inv_id, status='supported').all()
    ev = Evidence.query.filter_by(investigation_id=inv_id).all()
    logs = InvestigationLog.query.filter_by(investigation_id=inv_id).order_by(InvestigationLog.timestamp).all()
    state = _compute_state(inv_id)
    cmap = {c.id: c for c in confirmed}

    def clue_line(c):
        return {'clue_number': f"#{c.id:03d}", 'title': c.title, 'entity': c.entity,
                'signal': c.signal, 'confidence': c.confidence,
                'kind': ('AI INFERENCE' if c.clue_type in ('pattern', 'inference')
                         else 'FACT'),
                'source': c.source}
    primary = confirmed[0] if confirmed else None
    return jsonify({
        'case_name': inv.case_name if inv else '',
        'case_number': inv.case_number if inv else '',
        'summary': (f"{len(confirmed)} confirmed clue(s) and {len(rels)} supported "
                    f"relationship(s) were established. " +
                    (f"The strongest signal is: {primary.title}." if primary else
                     "No dominant signal has emerged yet.")),
        'primary_finding': (clue_line(primary) if primary else None),
        'evidence_used': [{'filename': e.filename, 'type': e.file_type} for e in ev],
        'key_clues': [clue_line(c) for c in confirmed],
        'timeline': [{'label': f"{c.title} — {c.source_location or c.source or ''}"} for c in confirmed if c.source_location],
        'relationships': [{'from': (cmap.get(r.source_clue_id).title if cmap.get(r.source_clue_id) else r.source_clue_id),
                           'to': (cmap.get(r.target_clue_id).title if cmap.get(r.target_clue_id) else r.target_clue_id),
                           'type': r.relationship_type, 'basis': r.evidence_basis} for r in rels],
        'hypotheses': ([{'text': f"The activity around {primary.entity or 'the flagged entity'} indicates {primary.signal.lower()}." ,
                         'status': ('SUPPORTED' if state['ready'] else 'TENTATIVE')}] if primary else []),
        'rejected_hypotheses': [{'title': c.title, 'reason': 'Marked NOT RELEVANT by the investigator.'} for c in rejected],
        'contradictions': [],
        'missing_evidence': state['missing'],
        'confidence': state['confidence'],
        'ready': state['ready'],
        'investigation_path': [{'step': l.step_type, 'content': (l.content or '').split(chr(10))[0]} for l in logs][-12:],
        'recommended_next_action': ("Prepare the case for review — the evidence supports a reliable conclusion."
                                    if state['ready'] else
                                    ("Obtain: " + "; ".join(state['missing']) if state['missing']
                                     else "Confirm more clues and connect them to raise confidence.")),
    })

@app.route('/api/investigations/<int:inv_id>/finalize', methods=['POST'])
def finalize_case(inv_id):
    """Complete the case: extract reusable memories and mark it solved."""
    from backend.models import Clue, Relationship, Investigation, Memory
    inv = db_session.get(Investigation, inv_id)
    if not inv:
        return jsonify(error="Case not found"), 404
    confirmed = Clue.query.filter_by(investigation_id=inv_id, status='confirmed').all()
    rels = Relationship.query.filter_by(investigation_id=inv_id, status='supported').all()
    owner = session.get('user_id') or inv.user_id
    added = 0
    # replace prior memories for this case so re-finalizing doesn't pile up
    Memory.query.filter_by(investigation_id=inv_id).delete()
    db_session.commit()
    # pattern memories from pattern-type clues + entities
    entities = sorted({c.entity for c in confirmed if c.entity})
    pattern_clues = [c for c in confirmed if c.clue_type == 'pattern'] or confirmed[:1]
    for c in pattern_clues[:2]:
        val = f"{c.signal or c.title}." + (f" Related entities: {', '.join(entities[:3])}." if entities else '')
        store_memory(int(owner) if owner else None,
                     key=f"Pattern: {c.title}", value=val, investigation_id=inv_id)
        added += 1
    if entities:
        store_memory(int(owner) if owner else None,
                     key=f"Entities in {inv.case_number}",
                     value=f"{', '.join(entities[:5])} appeared together with {len(rels)} supported link(s).",
                     investigation_id=inv_id)
        added += 1
    inv.status = 'solved'
    db_session.commit()
    return jsonify(success=True, memories_added=added, state=_compute_state(inv_id))

# ── Error Handlers ───────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="The trail has gone cold. Resource not found."), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify(error="An unexpected disturbance in the investigation."), 500

# ── Entry Point ──────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  NOCTRA — Beyond the Obvious.")
    print("  Investigation Bureau — Est. 2026")
    print("  Server: http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)
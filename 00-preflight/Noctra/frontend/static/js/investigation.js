/* ═══════════════════════════════════════════════════════════════════
   NOCTRA — Investigation Flow
   Screens 5 (Create), 6 (Workspace), 7 (Case Report)
═══════════════════════════════════════════════════════════════════ */

import { createOrion, initOrionBehavior, orionSpeak, orionReact, orionGlance, setOrionState,
         orionLeanIn, orionFlyTo, orionFlyOut, orionSpreadWings } from './orion.js';
import { initVoiceInvestigator, narrate } from './voice.js';

/* ── Orion Hint (shared between intake + workspace) ────────────────── */
function buildHintButton(getHint, solveOption) {
  if (document.getElementById('noc-hint-btn')) return;
  const btn = document.createElement('button');
  btn.id = 'noc-hint-btn';
  btn.className = 'noc-hint-btn';
  btn.innerHTML = '<span class="noc-hint-icon">?</span>Stuck? Ask Orion';
  document.body.appendChild(btn);

  const bubble = document.createElement('div');
  bubble.id = 'noc-hint-bubble';
  bubble.className = 'noc-hint-bubble';
  document.body.appendChild(bubble);

  function renderBubble(text) {
    bubble.innerHTML = `
      <button class="noc-hint-close" aria-label="Close">×</button>
      <div class="noc-hint-eyebrow">Orion's Hint</div>
      <div class="noc-hint-text">${escHtml(text)}</div>
      ${solveOption ? `<button class="noc-hint-solve" id="noc-hint-solve-btn">${escHtml(solveOption.label)}</button>` : ''}`;
    bubble.querySelector('.noc-hint-close').addEventListener('click', () => bubble.classList.remove('show'));
    if (solveOption) {
      bubble.querySelector('#noc-hint-solve-btn').addEventListener('click', async (e) => {
        const b = e.currentTarget;
        b.disabled = true; b.textContent = solveOption.busyLabel || 'Working…';
        try { await solveOption.run(); } finally { bubble.classList.remove('show'); }
      });
    }
  }

  let busy = false;
  btn.addEventListener('click', async () => {
    if (busy) {
      bubble.classList.toggle('show');
      return;
    }
    busy = true;
    bubble.classList.add('show');
    bubble.innerHTML = '<div class="noc-hint-eyebrow">Orion\'s Hint</div><div class="noc-hint-text">Thinking it over…</div>';
    let text = "Nothing comes to mind yet — take another look at what you have.";
    try { text = await getHint(); } catch (_) {}
    renderBubble(text);
    orionSpeak(text);
    if (window.NOCTRAVoice) window.NOCTRAVoice.narrate(text);
    busy = false;
  });
}

/* ─── Screen 5: Create Investigation ──────────────────────────────── */
function initCreateInvestigation() {
  createOrion('orion-create');
  initOrionBehavior();

  const dropzone = document.getElementById('evidence-dropzone');
  const fileInput = document.getElementById('evidence-input');
  const listEl = document.getElementById('evidence-list');
  const form = document.getElementById('case-form');
  const errorEl = document.getElementById('case-error');
  const btn = document.getElementById('btn-begin');

  let files = [];

  function typeTag(name) {
    const ext = (name.split('.').pop() || '').toLowerCase();
    if (ext === 'csv') return 'CSV';
    if (ext === 'pdf') return 'PDF';
    if (['png', 'jpg', 'jpeg'].includes(ext)) return 'IMAGE';
    if (['mp3', 'wav'].includes(ext)) return 'AUDIO';
    return 'NOTES';
  }

  function renderList() {
    listEl.innerHTML = files.map((f, i) => `
      <div class="evidence-list-item">
        <span>${f.name}</span>
        <span><span class="ev-tag">${typeTag(f.name)}</span><span class="ev-remove" data-i="${i}">✕</span></span>
      </div>
    `).join('');
    listEl.querySelectorAll('.ev-remove').forEach(el => {
      el.addEventListener('click', () => {
        files.splice(parseInt(el.dataset.i, 10), 1);
        renderList();
      });
    });
  }

  dropzone.addEventListener('click', () => fileInput.click());
  dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('drag-over'); });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-over'));
  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
    files.push(...Array.from(e.dataTransfer.files));
    renderList();
  });
  fileInput.addEventListener('change', () => {
    files.push(...Array.from(fileInput.files));
    renderList();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorEl.style.display = 'none';
    const caseName = document.getElementById('case-name').value.trim();
    const description = document.getElementById('case-description').value.trim();

    if (!caseName) {
      errorEl.textContent = 'A case name is required to open the file.';
      errorEl.style.display = 'block';
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Opening the case…';

    try {
      const res = await fetch('/api/investigations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_name: caseName, description })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Could not open the case file.');

      for (const f of files) {
        const fd = new FormData();
        fd.append('file', f);
        await fetch(`/api/investigations/${data.id}/evidence`, { method: 'POST', body: fd });
      }

      orionSpeak("The file is open. Let's see what it holds.");
      window.location.href = `/investigation/${data.id}/evidence`;
    } catch (err) {
      errorEl.textContent = err.message || 'Something disrupted the filing process.';
      errorEl.style.display = 'block';
      btn.disabled = false;
      btn.textContent = 'Begin Investigation';
    }
  });
}

/* ─── Screen 5b: Evidence Intake (Phase 1) ────────────────────────── */
function initEvidenceIntake() {
  const screen = document.getElementById('evidence-intake-screen');
  const invId = screen.dataset.investigationId;

  createOrion('orion-intake');
  initOrionBehavior();

  const dropzone = document.getElementById('intake-dropzone');
  const fileInput = document.getElementById('intake-file-input');
  const listEl = document.getElementById('intake-evidence-list');
  const continueBtn = document.getElementById('btn-continue-board');
  const hint = document.querySelector('.intake-hint');

  function typeTag(name) {
    const ext = (name.split('.').pop() || '').toLowerCase();
    if (ext === 'csv') return 'CSV';
    if (ext === 'pdf') return 'PDF';
    if (['png', 'jpg', 'jpeg'].includes(ext)) return 'IMAGE';
    if (['mp3', 'wav'].includes(ext)) return 'AUDIO';
    if (['doc', 'docx'].includes(ext)) return 'DOCX';
    return 'NOTES';
  }

  function updateContinueState(items) {
    const ready = items.length > 0;
    continueBtn.classList.toggle('btn-disabled', !ready);
    hint.textContent = ready
      ? 'Evidence recorded. Continue when you are ready.'
      : 'Add at least one exhibit to continue.';
  }

  function clueRow(clue) {
    if (clue.status === 'confirmed') {
      return `
        <div class="clue-row clue-row-confirmed" data-cid="${clue.id}">
          <div class="clue-row-head">
            <span class="clue-number">CLUE ${clue.clue_number}</span>
            <span class="clue-confidence">${clue.confidence}%</span>
          </div>
          <div class="clue-title">${escHtml(clue.title)}</div>
          <div class="clue-meta">SOURCE: ${escHtml(clue.source || '')} · ENTITY: ${escHtml(clue.entity || '—')} · SIGNAL: ${escHtml(clue.signal || '')}</div>
        </div>`;
    }
    if (clue.status === 'rejected') {
      return `
        <div class="clue-row clue-row-rejected" data-cid="${clue.id}">
          <div class="clue-title">${escHtml(clue.title)}</div>
          <span class="clue-rejected-tag">Not relevant</span>
        </div>`;
    }
    return `
      <div class="clue-row clue-row-candidate" data-cid="${clue.id}">
        <div class="clue-row-head">
          <span class="clue-flag">SUSPICIOUS ACTIVITY?</span>
          <span class="clue-confidence">${clue.confidence}%</span>
        </div>
        <div class="clue-title">${escHtml(clue.title)}</div>
        <div class="clue-actions">
          <button class="clue-btn clue-btn-mark" data-cid="${clue.id}" data-action="confirm">Mark as Clue</button>
          <button class="clue-btn clue-btn-reject" data-cid="${clue.id}" data-action="reject">Not Relevant</button>
          <button class="clue-btn clue-btn-inspect" data-cid="${clue.id}" data-action="inspect">Inspect</button>
        </div>
      </div>`;
  }

  function docCard(item) {
    let statusHtml, cluesHtml = '';
    if (!item.analyzed) {
      statusHtml = `<span class="intake-doc-status is-analyzing">ANALYZING…</span>`;
    } else {
      const clues = item.candidate_clues || [];
      const activeCount = clues.filter(c => c.status !== 'rejected').length;
      statusHtml = `<span class="intake-doc-status is-complete">ANALYSIS COMPLETE</span>`;
      const summary = clues.length
        ? `${activeCount} potential clue${activeCount === 1 ? '' : 's'} discovered.`
        : `No potential clues discovered.`;
      cluesHtml = `<div class="intake-doc-clues">${summary}</div>`;
      if (clues.length) {
        cluesHtml += `<div class="clue-row-list">${clues.map(clueRow).join('')}</div>`;
      }
    }
    return `
      <div class="intake-doc" data-eid="${item.id}">
        <div class="intake-doc-main">
          <div class="intake-doc-name">${escHtml(item.filename)}</div>
          <div class="intake-doc-meta">
            <span class="intake-doc-type">${(item.file_type || 'notes').toUpperCase()}</span>
            ${statusHtml}
          </div>
          ${cluesHtml}
        </div>
      </div>`;
  }

  function attachClueHandlers(scope) {
    scope.querySelectorAll('.clue-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const cid = btn.dataset.cid;
        const action = btn.dataset.action;
        if (action === 'inspect') {
          inspectClue(cid);
          return;
        }
        btn.closest('.clue-actions').querySelectorAll('.clue-btn').forEach(b => b.disabled = true);
        try {
          await fetch(`/api/clues/${cid}/decision`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
          });
          if (action === 'confirm') orionReact('relationship');
          await loadAndRender();
          await renderClueTray();
        } catch (_) { /* leave buttons as-is on failure */ }
      });
    });
  }

  async function inspectClue(cid) {
    let clue;
    try {
      const items = await (await fetch(`/api/investigations/${invId}/evidence`)).json();
      for (const it of items) {
        const found = (it.candidate_clues || []).find(c => String(c.id) === String(cid));
        if (found) { clue = found; break; }
      }
    } catch (_) { /* fall through */ }
    if (!clue) return;
    const body = `
      <div class="noc-preview-text">${escHtml(clue.description || '')}</div>
      <div style="margin-top:14px;font-family:'Courier Prime',monospace;font-size:13px;color:rgba(90,56,16,0.85);">
        SOURCE: ${escHtml(clue.source || '')}<br>
        ENTITY: ${escHtml(clue.entity || '—')}<br>
        SIGNAL: ${escHtml(clue.signal || '')}<br>
        CONFIDENCE: ${clue.confidence}%
      </div>`;
    showModal(clue.title, 'Candidate Clue', body);
  }

  async function loadAndRender() {
    let items = [];
    try {
      items = await (await fetch(`/api/investigations/${invId}/evidence`)).json();
    } catch (_) { items = []; }

    if (!items.length) {
      listEl.innerHTML = '<div class="intake-empty">No evidence added yet.</div>';
      updateContinueState(items);
      return;
    }
    listEl.innerHTML = items.map(docCard).join('');
    attachClueHandlers(listEl);
    updateContinueState(items);

    // Kick off analysis for anything not yet analyzed.
    const pending = items.filter(i => !i.analyzed);
    for (const item of pending) {
      try {
        const res = await fetch(`/api/investigations/${invId}/evidence/${item.id}/analyze`, { method: 'POST' });
        const result = await res.json();
        const card = listEl.querySelector(`.intake-doc[data-eid="${item.id}"]`);
        if (card) {
          const count = (result.candidate_clues || []).length;
          const rendered = docCard({ id: item.id, filename: item.filename, file_type: item.file_type, analyzed: true, candidate_clues: result.candidate_clues || [] });
          const wrapper = document.createElement('div');
          wrapper.innerHTML = rendered.trim();
          const newCard = wrapper.firstChild;
          card.replaceWith(newCard);
          attachClueHandlers(newCard);
          if (count > 0) orionGlance(window.innerWidth / 2);
        }
      } catch (_) { /* leave as analyzing; investigator can retry by reloading */ }
    }
  }

  async function renderClueTray() {
    let confirmed = [];
    try {
      confirmed = await (await fetch(`/api/investigations/${invId}/clues?status=confirmed`)).json();
    } catch (_) { confirmed = []; }
    let tray = document.getElementById('clue-tray');
    if (!confirmed.length) {
      if (tray) tray.remove();
      return;
    }
    if (!tray) {
      tray = document.createElement('div');
      tray.id = 'clue-tray';
      tray.className = 'clue-tray';
      document.getElementById('evidence-intake-screen').insertBefore(tray, document.querySelector('.intake-footer'));
    }
    tray.innerHTML = `
      <div class="clue-tray-title">Clue Collection</div>
      <div class="clue-tray-items">
        ${confirmed.map(c => `<div class="clue-chip">CLUE ${c.clue_number} — ${escHtml(c.title)}</div>`).join('')}
      </div>`;
  }

  async function uploadFiles(files) {
    for (const f of files) {
      const fd = new FormData();
      fd.append('file', f);
      try {
        await fetch(`/api/investigations/${invId}/evidence`, { method: 'POST', body: fd });
      } catch (_) { /* skip failed upload, keep going */ }
    }
    orionSpeak(files.length === 1 ? 'New evidence, noted.' : 'New evidence, noted — let me look these over.');
    await loadAndRender();
  }

  dropzone.addEventListener('click', () => fileInput.click());
  dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('drag-over'); });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-over'));
  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files);
    if (files.length) uploadFiles(files);
  });
  fileInput.addEventListener('change', () => {
    const files = Array.from(fileInput.files);
    if (files.length) uploadFiles(files);
    fileInput.value = '';
  });

  continueBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    if (continueBtn.classList.contains('btn-disabled')) return;
    const href = continueBtn.getAttribute('href');
    setOrionState('alert');
    orionSpeak('Good. Let me carry these to the board.');
    await orionFlyOut('across');
    window.location.href = href;
  });

  loadAndRender();
  renderClueTray();

  buildHintButton(async () => {
    let items = [];
    try { items = await (await fetch(`/api/investigations/${invId}/evidence`)).json(); } catch (_) {}
    if (!items.length) return "Start by adding your evidence — drop a file above and I'll take a look.";
    if (items.some(i => !i.analyzed)) return "Give me a moment — I'm still going over one of the exhibits.";
    const allClues = items.flatMap(i => i.candidate_clues || []);
    const candidates = allClues.filter(c => c.status !== 'confirmed' && c.status !== 'rejected');
    if (candidates.length) {
      const top = [...candidates].sort((a, b) => (b.confidence || 0) - (a.confidence || 0))[0];
      return `You have ${candidates.length} candidate clue${candidates.length === 1 ? '' : 's'} still waiting on a decision. Start with "${top.title}" — it's flagged at ${top.confidence}%.`;
    }
    const confirmed = allClues.filter(c => c.status === 'confirmed');
    if (!confirmed.length) return "Nothing has been marked as a clue yet. Look for whatever felt out of place and mark it — you can always change your mind later on the board.";
    return "Everything here has been reviewed. Continue to the Evidence Board when you're ready.";
  }, {
    label: 'Let Orion Decide & Continue',
    busyLabel: 'Reviewing exhibits…',
    run: async () => {
      let items = [];
      try { items = await (await fetch(`/api/investigations/${invId}/evidence`)).json(); } catch (_) {}
      const candidates = items.flatMap(i => i.candidate_clues || []).filter(c => c.status !== 'confirmed' && c.status !== 'rejected');
      for (const c of candidates) {
        try {
          await fetch(`/api/clues/${c.id}/decision`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: c.confidence >= 50 ? 'confirm' : 'reject' })
          });
        } catch (_) {}
      }
      orionSpeak("I've weighed every candidate. Taking us to the board.");
      await orionFlyOut('across');
      window.location.href = `/investigation/${invId}`;
    }
  });
}

/* ─── Screen 6: Interactive Evidence Board (Phases 4–13) ──────────── */
function initWorkspace() {
  const screen = document.getElementById('workspace-screen');
  const invId = screen.dataset.investigationId;
  createOrion('orion-workspace');
  initOrionBehavior();

  const canvas = document.getElementById('board-canvas');
  const strings = document.getElementById('board-strings');
  const stickyLayer = document.getElementById('sticky-layer');
  const emptyEl = document.getElementById('board-empty');
  const trayList = document.getElementById('tray-list');
  const fill = document.getElementById('confidence-fill');
  const pct = document.getElementById('confidence-pct');
  const reportBtn = document.getElementById('btn-case-report');
  const reviewBtn = document.getElementById('btn-review-evidence');
  const patternsBtn = document.getElementById('btn-check-patterns');
  const alertHost = document.getElementById('orion-alert');

  let board = { clues: [], relationships: [], state: {} };
  let liveLine = '';
  let lastReady = false;
  const dismissedMissing = new Set();
  const dismissedPatterns = new Set();

  const CARD_W = 90, CARD_H = 38; // half-size, for centring strings

  function clueById(id) { return board.clues.find(c => c.id === id); }

  // subtle Orion gestures
  function orionNod() {
    const h = document.getElementById('orionHead'); if (!h) return;
    h.style.transition = 'transform .2s'; h.style.transform = 'translateY(4px)';
    setTimeout(() => { h.style.transform = 'translateY(0)'; }, 220);
  }
  function orionShakeHead() {
    const h = document.getElementById('orionHead'); if (!h) return;
    const seq = ['-11deg', '11deg', '-7deg', '3deg', '0deg']; let i = 0;
    const t = setInterval(() => { h.style.transition = 'transform .1s'; h.style.transform = `rotate(${seq[i]})`; if (++i >= seq.length) clearInterval(t); }, 110);
  }

  function toast(title, msg, kind) {
    let t = document.getElementById('board-toast');
    if (!t) { t = document.createElement('div'); t.id = 'board-toast'; t.className = 'board-toast'; document.body.appendChild(t); }
    t.className = 'board-toast show ' + (kind || '');
    t.innerHTML = `<div class="bt-title">${escHtml(title)}</div><div class="bt-msg">${escHtml(msg || '')}</div>`;
    clearTimeout(t._t); t._t = setTimeout(() => t.classList.remove('show'), 3400);
  }

  async function refresh() {
    try { board = await (await fetch(`/api/investigations/${invId}/board`)).json(); }
    catch (_) { return; }
    render();
    updateState(board.state);
    checkMissingAndPatterns();
  }

  const MAIN_THRESHOLD = 75;
  function isMainClue(c) { return (c.confidence || 0) >= MAIN_THRESHOLD; }

  // ---- Case Files (every confirmed clue — placed or not) ----
  function renderTray() {
    if (!board.clues.length) {
      trayList.innerHTML = '<div class="tray-empty">No confirmed clues yet. Return to the Evidence Desk to mark clues.</div>';
      return;
    }
    const sorted = [...board.clues].sort((a, b) => (b.confidence || 0) - (a.confidence || 0));
    trayList.innerHTML = sorted.map(c => `
      <div class="tray-clue ${c.placed ? 'is-onboard' : ''} ${isMainClue(c) ? 'is-main' : ''}" data-cid="${c.id}">
        ${isMainClue(c) ? '<span class="tray-main-badge">MAIN</span>' : ''}
        <div class="tray-clue-head"><span class="tray-clue-num">CLUE ${c.clue_number}${c.origin === 'previous_case' ? ' · PATTERN' : ''}</span><span class="tray-clue-conf">${c.confidence}%</span></div>
        <div class="tray-clue-title">${escHtml(c.title)}</div>
        <div class="tray-clue-entity">${escHtml(c.entity || '—')}</div>
        <div class="tray-clue-foot">
          <span class="tray-status-tag">${c.placed ? '● On Board' : '○ In Files'}</span>
          <span class="tray-clue-actions">
            <button class="tray-mini-btn" data-act="view" title="View clue">View</button>
            <button class="tray-mini-btn" data-act="toggle" title="${c.placed ? 'Return to files' : 'Place on board'}">${c.placed ? 'Unpin' : 'Place'}</button>
          </span>
        </div>
      </div>`).join('');
    trayList.querySelectorAll('.tray-clue').forEach(el => {
      const cid = el.dataset.cid;
      el.addEventListener('pointerdown', e => {
        if (e.target.closest('.tray-mini-btn')) return;
        startTrayDrag(e, cid);
      });
      el.querySelector('[data-act="view"]').addEventListener('click', (e) => {
        e.stopPropagation();
        openClueModal(clueById(Number(cid)));
      });
      el.querySelector('[data-act="toggle"]').addEventListener('click', async (e) => {
        e.stopPropagation();
        const c = clueById(Number(cid));
        if (c.placed) {
          await placeClue(cid, c.x, c.y, false);
        } else {
          await placeClue(cid, 60 + Math.round(Math.random() * 120), 60 + Math.round(Math.random() * 120), true);
        }
        refresh();
      });
    });
  }

  function openClueModal(c) {
    if (!c) return;
    const sub = `${c.clue_number} · ${c.confidence}% confidence${isMainClue(c) ? ' · MAIN CLUE' : ''}`;
    const body = `
      <div class="noc-preview-text">
        <div style="font-family:'Cinzel',serif;font-size:16px;color:#4a3410;margin-bottom:10px;">${escHtml(c.title)}</div>
        <div style="margin-bottom:8px;">${escHtml(c.description || 'No further description recorded.')}</div>
        <div style="font-family:'Courier Prime',monospace;font-size:12px;color:#7a1a1a;">
          ENTITY: ${escHtml(c.entity || '—')}<br>
          SIGNAL: ${escHtml(c.signal || '—')}<br>
          SOURCE: ${escHtml(c.source || '—')}
        </div>
      </div>`;
    showModal(c.title, sub, body);
  }

  function startTrayDrag(e, cid) {
    e.preventDefault();
    const ghost = document.createElement('div');
    ghost.className = 'drag-ghost';
    ghost.textContent = (clueById(Number(cid)) || {}).title || 'CLUE';
    document.body.appendChild(ghost);
    const move = (ev) => { ghost.style.left = ev.clientX + 'px'; ghost.style.top = ev.clientY + 'px'; };
    move(e);
    const up = async (ev) => {
      document.removeEventListener('pointermove', move);
      document.removeEventListener('pointerup', up);
      ghost.remove();
      const r = canvas.getBoundingClientRect();
      if (ev.clientX >= r.left && ev.clientX <= r.right && ev.clientY >= r.top && ev.clientY <= r.bottom) {
        const x = Math.max(0, Math.round(ev.clientX - r.left - CARD_W));
        const y = Math.max(0, Math.round(ev.clientY - r.top - CARD_H));
        await placeClue(cid, x, y, true);
        orionReact('relationship'); orionNod();
        refresh();
      }
    };
    document.addEventListener('pointermove', move);
    document.addEventListener('pointerup', up);
  }

  async function placeClue(cid, x, y, placed) {
    try {
      await fetch(`/api/clues/${cid}/place`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x, y, placed })
      });
    } catch (_) {}
  }

  // ---- board render ----
  function render() {
    renderTray();
    const placed = board.clues.filter(c => c.placed);
    emptyEl.style.display = placed.length ? 'none' : 'block';
    canvas.querySelectorAll('.board-clue').forEach(n => n.remove());
    placed.forEach(c => {
      const el = document.createElement('div');
      el.className = 'board-clue' + (c.origin === 'previous_case' ? ' is-pattern' : '') + (isMainClue(c) ? ' is-main' : '');
      el.dataset.cid = c.id;
      el.style.left = (c.x || 60) + 'px';
      el.style.top = (c.y || 60) + 'px';
      el.innerHTML = `
        <div class="pin"></div>
        ${isMainClue(c) ? '<span class="board-main-badge">MAIN CLUE</span>' : ''}
        <div class="board-clue-num">CLUE ${c.clue_number}${c.origin === 'previous_case' ? ' · PATTERN' : ''}</div>
        <div class="board-clue-title">${escHtml(c.title)}</div>
        <div class="board-clue-entity">${escHtml(c.entity || '—')}</div>
        <div class="connect-handle" title="Drag to another clue to connect">↔</div>`;
      canvas.appendChild(el);
      el.addEventListener('dblclick', () => openClueModal(c));
      wireBoardClue(el, c);
    });
    drawStrings();
  }

  function drawStrings() {
    const placed = board.clues.filter(c => c.placed);
    const pos = {};
    placed.forEach(c => pos[c.id] = { x: (c.x || 60) + CARD_W, y: (c.y || 60) + CARD_H });
    let svg = '';
    board.relationships.forEach(r => {
      const a = pos[r.source], b = pos[r.target];
      const A = clueById(r.source), B = clueById(r.target);
      const mainLink = A && B && isMainClue(A) && isMainClue(B);
      if (a && b) svg += `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" class="string ${r.status}${mainLink ? ' main' : ''}" data-rid="${r.id}"/>`;
    });
    strings.innerHTML = svg + (liveLine || '');
    strings.querySelectorAll('line.string[data-rid]').forEach(l => {
      l.addEventListener('click', async () => {
        await fetch(`/api/relationships/${l.dataset.rid}`, { method: 'DELETE' });
        orionSpeak('Connection removed.'); refresh();
      });
    });
  }

  function wireBoardClue(el, c) {
    const handle = el.querySelector('.connect-handle');
    // reposition
    el.addEventListener('pointerdown', (e) => {
      if (e.target === handle) return;
      e.preventDefault();
      const sx = e.clientX, sy = e.clientY, ox = c.x || 60, oy = c.y || 60;
      try { el.setPointerCapture(e.pointerId); } catch (_) {}
      const move = (ev) => { c.x = ox + (ev.clientX - sx); c.y = oy + (ev.clientY - sy); el.style.left = c.x + 'px'; el.style.top = c.y + 'px'; drawStrings(); };
      const up = async () => { el.removeEventListener('pointermove', move); el.removeEventListener('pointerup', up); await placeClue(c.id, Math.round(c.x), Math.round(c.y), true); };
      el.addEventListener('pointermove', move);
      el.addEventListener('pointerup', up);
    });
    // connect
    handle.addEventListener('pointerdown', (e) => {
      e.preventDefault(); e.stopPropagation();
      const r = canvas.getBoundingClientRect();
      const from = { x: (c.x || 60) + CARD_W, y: (c.y || 60) + CARD_H };
      const move = (ev) => { liveLine = `<line x1="${from.x}" y1="${from.y}" x2="${ev.clientX - r.left}" y2="${ev.clientY - r.top}" class="string live"/>`; drawStrings(); };
      const up = async (ev) => {
        document.removeEventListener('pointermove', move);
        document.removeEventListener('pointerup', up);
        liveLine = '';
        const target = document.elementFromPoint(ev.clientX, ev.clientY);
        const targetCard = target && target.closest('.board-clue');
        if (targetCard && Number(targetCard.dataset.cid) !== c.id) {
          await tryConnect(c.id, Number(targetCard.dataset.cid));
        } else { drawStrings(); }
      };
      document.addEventListener('pointermove', move);
      document.addEventListener('pointerup', up);
    });
  }

  async function tryConnect(a, b) {
    let res;
    try {
      res = await (await fetch(`/api/investigations/${invId}/connect`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: a, target: b })
      })).json();
    } catch (_) { drawStrings(); return; }

    if (res.status === 'supported') {
      if (!res.duplicate) board.relationships.push({ id: res.id, source: a, target: b, type: res.type, status: 'supported', basis: res.basis });
      drawStrings(); orionNod(); orionSpeak('That connection is supported.');
      toast('SUPPORTED CONNECTION', res.basis, 'ok');
      updateState(res.state); checkMissingAndPatterns();
    } else {
      const A = clueById(a), B = clueById(b);
      const pa = { x: (A.x || 60) + CARD_W, y: (A.y || 60) + CARD_H };
      const pb = { x: (B.x || 60) + CARD_W, y: (B.y || 60) + CARD_H };
      strings.innerHTML += `<line x1="${pa.x}" y1="${pa.y}" x2="${pb.x}" y2="${pb.y}" class="string rejected flicker"/>`;
      orionShakeHead(); orionSpeak('These pieces do not connect yet.');
      toast('CONNECTION NOT SUPPORTED', res.basis, 'bad');
      setTimeout(drawStrings, 950);
    }
  }

  function updateState(state) {
    if (!state) return;
    board.state = state;
    const c = state.confidence || 0;
    fill.style.width = c + '%';
    pct.textContent = c + '%';
    fill.className = 'confidence-fill' + (c >= 70 ? ' high' : c >= 45 ? ' mid' : '');
    if (state.ready) {
      reportBtn.classList.remove('report-locked');
      if (!lastReady) { lastReady = true; onReady(); }
    } else {
      reportBtn.classList.add('report-locked');
      lastReady = false;
    }
  }

  async function onReady() {
    setOrionState('alert');
    orionSpeak('The case is ready for review.');
    narrate('The case is ready for review.');
    await orionFlyTo(reportBtn, { hold: 500 });
    reportBtn.classList.add('report-armed');
  }

  async function checkMissingAndPatterns() {
    try {
      const m = await (await fetch(`/api/investigations/${invId}/missing`)).json();
      if (m.missing && !dismissedMissing.has(m.message)) { showMissing(m); return; }
    } catch (_) {}
    try {
      const ps = await (await fetch(`/api/investigations/${invId}/patterns`)).json();
      const fresh = ps.find(p => !dismissedPatterns.has(p.previous_case + '|' + p.current_clue));
      if (fresh) { showPattern(fresh); return; }
    } catch (_) {}
    hideAlert();
  }

  function hideAlert() { alertHost.style.display = 'none'; alertHost.innerHTML = ''; }

  function showMissing(m) {
    orionLeanIn(); orionSpeak("Something doesn't add up.");
    alertHost.style.display = 'block';
    alertHost.className = 'orion-alert alert-missing';
    alertHost.innerHTML = `
      <div class="alert-eyebrow">Missing Link</div>
      <div class="alert-title">${escHtml(m.title)}</div>
      <div class="alert-msg">${escHtml(m.message)}</div>
      <div class="alert-actions">
        <button class="alert-btn" id="al-review">Review Evidence</button>
        <button class="alert-btn ghost" id="al-cont">Continue Investigation</button>
      </div>`;
    document.getElementById('al-review').onclick = flyToEvidence;
    document.getElementById('al-cont').onclick = () => { dismissedMissing.add(m.message); checkMissingAndPatterns(); };
  }

  function showPattern(p) {
    orionSpeak("I've found a similar pattern."); setOrionState('alert');
    alertHost.style.display = 'block';
    alertHost.className = 'orion-alert alert-pattern';
    alertHost.innerHTML = `
      <div class="alert-eyebrow">Similar Pattern Detected · ${p.similarity}%</div>
      <div class="alert-title">${escHtml(p.current_clue)} &nbsp;↔&nbsp; ${escHtml(p.previous_case)}</div>
      <div class="alert-msg">${escHtml(p.previous_pattern || '')}</div>
      <div class="alert-actions">
        <button class="alert-btn" id="al-inspect">Inspect Previous Case</button>
        <button class="alert-btn ghost" id="al-ignore">Ignore</button>
      </div>`;
    document.getElementById('al-inspect').onclick = async () => {
      const s = p.suggested || {};
      try {
        await fetch(`/api/investigations/${invId}/patterns/adopt`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            previous_case: p.previous_case, title: s.title || ('Pattern: ' + p.current_clue),
            description: s.description || p.previous_pattern, entity: s.entity || p.current_entity,
            confidence: s.confidence || p.similarity
          })
        });
      } catch (_) {}
      orionSpeak('I found a related pattern — added to your clues.');
      toast('CLUE ADDED', 'A pattern clue from ' + p.previous_case + ' was added to your tray.', 'ok');
      dismissedPatterns.add(p.previous_case + '|' + p.current_clue);
      refresh();
    };
    document.getElementById('al-ignore').onclick = () => { dismissedPatterns.add(p.previous_case + '|' + p.current_clue); checkMissingAndPatterns(); };
  }

  async function flyToEvidence() {
    orionSpeak('Back to the evidence.');
    await orionFlyOut('across');
    window.location.href = `/investigation/${invId}/evidence`;
  }

  reviewBtn.onclick = flyToEvidence;
  patternsBtn.onclick = async () => {
    let ps = [];
    try { ps = await (await fetch(`/api/investigations/${invId}/patterns`)).json(); } catch (_) {}
    const fresh = ps.find(p => !dismissedPatterns.has(p.previous_case + '|' + p.current_clue));
    if (fresh) showPattern(fresh);
    else { orionSpeak('No matching patterns in the archive yet.'); toast('NO PATTERNS', 'Nothing in previous cases resembles these clues yet.', 'ok'); }
  };

  // The report is always reachable — an unfinished case still gets a
  // report, it's just clearly marked UNFINISHED with the missing clues
  // listed at the bottom, instead of blocking navigation entirely.
  reportBtn.addEventListener('click', (e) => {
    if (reportBtn.classList.contains('report-locked')) {
      orionSpeak('The case is not fully closed yet — the report will show what is still missing.');
      toast('REPORT NOT FINAL', 'Opening the report as-is — it will be marked UNFINISHED with what\'s still missing.', 'ok');
    }
  });

  initVoiceInvestigator({
    onCommand: (t) => {
      const s = t.toLowerCase();
      if (/review|evidence|back/.test(s)) flyToEvidence();
      else if (/pattern|previous|similar/.test(s)) patternsBtn.click();
      else if (/report|ready|conclude/.test(s)) reportBtn.click();
      else narrate('Command noted.');
    }
  });

  initCaseOptions(invId);
  buildNotebook(invId, canvas, stickyLayer);
  buildHintButton(async () => {
    try {
      const m = await (await fetch(`/api/investigations/${invId}/missing`)).json();
      if (m.missing) return m.message || m.title || "Something doesn't add up yet.";
    } catch (_) {}
    try {
      const ps = await (await fetch(`/api/investigations/${invId}/patterns`)).json();
      if (ps.length) return `This resembles ${ps[0].previous_case} — worth a look under "Check Previous Cases."`;
    } catch (_) {}
    const placed = board.clues.filter(c => c.placed);
    if (!placed.length) return "Pull a clue from Case Files onto the board to get started.";
    if (!board.relationships.length) return "Try connecting two clues that reference the same entity or come from the same exhibit — that's usually where a case opens up.";
    if (board.state && (board.state.confidence || 0) < 70) return "The connections you have aren't quite enough yet. Check Case Files for a clue you haven't placed — it may be the missing piece.";
    return "This case is holding together well. Check the Case Report when you're ready.";
  }, {
    label: 'Let Orion Solve It From Here',
    busyLabel: 'Investigating…',
    run: () => autoSolveCase()
  });

  async function autoSolveCase() {
    orionSpeak('Let me take this from here.');
    toast('ORION INVESTIGATING', 'Placing every clue and testing each possible connection…', 'ok');

    // 1. bring any confirmed-but-unplaced clues onto the board, grid-arranged
    const cols = Math.max(1, Math.floor((canvas.clientWidth - 60) / 210));
    let i = 0;
    for (const c of board.clues) {
      if (!c.placed) {
        const col = i % cols, row = Math.floor(i / cols);
        await placeClue(c.id, 30 + col * 210, 30 + row * 130, true);
      }
      i++;
    }
    await refresh();

    // 2. attempt a connection between every pair of clues — the same
    //    evidence-based check a manual string-pull would trigger, just exhaustive
    const ids = board.clues.map(c => c.id);
    for (let a = 0; a < ids.length; a++) {
      for (let b = a + 1; b < ids.length; b++) {
        try {
          await fetch(`/api/investigations/${invId}/connect`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source: ids[a], target: ids[b] })
          });
        } catch (_) {}
      }
    }
    await refresh();

    if (board.state && board.state.ready) {
      orionSpeak('Case solved. Moving to the report.');
      toast('CASE SOLVED', 'Every supported connection has been made — opening the report.', 'ok');
      setTimeout(() => { window.location.href = `/investigation/${invId}/report`; }, 1400);
    } else {
      // Still stuck after Orion did everything the evidence allows — don't
      // leave the investigator at a dead end. Generate the report anyway;
      // it will be clearly marked UNFINISHED with exactly what's missing.
      const missing = (board.state && board.state.missing) || [];
      orionSpeak("I've taken this as far as the current evidence allows. Let me write up what we have so far.");
      toast('REPORT GENERATED — UNFINISHED', missing.length ? missing[0] : 'More evidence is needed to close this case — the report lists what\'s missing.', 'bad');
      setTimeout(() => { window.location.href = `/investigation/${invId}/report`; }, 1600);
    }
  }

  orionSpeak('Drag your clues onto the board, then connect the ones that belong together.');
  refresh();

  // ---- Case Options dropdown ----
  function initCaseOptions(id) {
    const btn = document.getElementById('btn-case-options');
    const menu = document.getElementById('case-options-menu');
    const listEl = document.getElementById('com-case-list');
    if (!btn || !menu) return;

    function close() { menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); }
    function open() { menu.hidden = false; btn.setAttribute('aria-expanded', 'true'); loadCases(); }

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (menu.hidden) open(); else close();
    });
    document.addEventListener('click', (e) => { if (!menu.hidden && !menu.contains(e.target)) close(); });

    async function loadCases() {
      let items = [];
      try { items = await (await fetch('/api/investigations')).json(); } catch (_) {}
      const others = items.filter(i => i.id !== Number(id));
      listEl.innerHTML = others.length
        ? others.slice(0, 8).map(i => `<a class="com-item com-case" href="/investigation/${i.id}">${escHtml(i.case_name)}<span class="com-case-num">${escHtml(i.case_number)}</span></a>`).join('')
        : '<div class="com-empty">No other open cases.</div>';
    }

    document.getElementById('com-arrange').addEventListener('click', async () => {
      const cols = Math.max(1, Math.floor((canvas.clientWidth - 60) / 210));
      let i = 0;
      for (const c of board.clues) {
        const col = i % cols, row = Math.floor(i / cols);
        await placeClue(c.id, 30 + col * 210, 30 + row * 130, true);
        i++;
      }
      orionSpeak('Board arranged.');
      close();
      refresh();
    });

    document.getElementById('com-highlight').addEventListener('click', () => {
      canvas.classList.toggle('highlight-main');
      close();
    });
  }
}

/* ─── Screen 7: Case Report ────────────────────────────────────────── */
/* ─── Screen 7: Case Report (clue-based, Phase 14) ────────────────── */
async function initReport() {
  const screen = document.getElementById('report-screen');
  const invId = screen.dataset.investigationId;
  createOrion('orion-report');
  initOrionBehavior();

  const esc = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  let rep;
  try { rep = await (await fetch(`/api/investigations/${invId}/case-report`)).json(); }
  catch (_) { rep = null; }

  const sheet = document.querySelector('.report-sheet');
  const footer = sheet ? sheet.querySelector('.report-footer') : null;
  const metricsEl = document.getElementById('report-metrics');
  const evidenceEl = document.getElementById('report-evidence');
  const timelineEl = document.getElementById('report-timeline');
  const assessmentEl = document.getElementById('report-assessment');
  const summaryEl = document.querySelector('.report-summary');

  document.getElementById('btn-export-pdf')?.addEventListener('click', () => window.print());
  initVoiceInvestigator({ onCommand: (t) => narrate(rep ? rep.summary : 'No report yet.') });

  if (!rep) { assessmentEl.textContent = 'The case report could not be loaded.'; return; }

  // Clear status stamp — COMPLETED vs UNFINISHED, shown at the very top,
  // easy to understand at a glance (written + visually animated).
  const stampSlot = document.getElementById('report-status-stamp-slot');
  if (stampSlot) {
    stampSlot.innerHTML = rep.ready
      ? `<div class="report-status-stamp is-complete"><span class="stamp-dot"></span>COMPLETED — Case Fully Documented</div>`
      : `<div class="report-status-stamp is-unfinished"><span class="stamp-dot"></span>UNFINISHED — Investigation Still Open</div>`;
  }

  if (summaryEl) summaryEl.textContent = rep.summary || '—';

  // Quick Look sidebar — mirrors the status stamp + confidence so it's
  // readable at a glance without scrolling through the full report.
  const qlStatus = document.getElementById('quicklook-status');
  const qlConfidence = document.getElementById('quicklook-confidence');
  if (qlStatus) {
    qlStatus.textContent = rep.ready ? '✔ COMPLETED' : '⚠ UNFINISHED';
    qlStatus.className = 'quicklook-status ' + (rep.ready ? 'is-complete' : 'is-unfinished');
  }
  if (qlConfidence) qlConfidence.textContent = `Confidence: ${rep.confidence || 0}%`;

  // Confidence + readiness
  const c = rep.confidence || 0;
  metricsEl.innerHTML = `
    <div class="metric-item">
      <div class="metric-label">Case Confidence</div>
      <div class="metric-bar"><div class="metric-bar-fill" style="width:${c}%;"></div></div>
      <div class="metric-value">${c}%</div>
    </div>
    <div style="font-family:'Courier Prime',monospace;font-size:13px;margin-top:8px;color:${rep.ready ? '#2a6a2a' : '#7a1a1a'};">
      ${rep.ready ? 'STATUS: Conclusion-ready' : 'STATUS: Further investigation required'}
    </div>`;

  evidenceEl.innerHTML = (rep.evidence_used || []).length
    ? rep.evidence_used.map(e => `<li>${esc(e.filename)} <em style="opacity:.6;">(${esc(e.type || 'notes')})</em></li>`).join('')
    : '<li class="panel-empty">No evidence on file.</li>';

  timelineEl.innerHTML = (rep.timeline || []).length
    ? rep.timeline.map(t => `<li>${esc(t.label)}</li>`).join('')
    : '<li class="panel-empty">No dated events recorded.</li>';

  // Primary finding + recommended next action into the assessment block
  const pf = rep.primary_finding;
  assessmentEl.innerHTML = (pf
    ? `<div style="font-family:'Cormorant Garamond',serif;font-size:18px;color:#3a2a12;margin-bottom:8px;">
         Primary finding: <strong>${esc(pf.title)}</strong>${pf.entity ? ' — ' + esc(pf.entity) : ''}
         <span class="kind-tag kind-${pf.kind === 'FACT' ? 'fact' : 'inference'}">${esc(pf.kind)}</span>
       </div>` : '')
    + `<div style="font-family:'Courier Prime',monospace;font-size:13px;color:#5a4a2e;">RECOMMENDED NEXT ACTION</div>
       <div style="font-family:'Cormorant Garamond',serif;font-size:16px;color:#4a3410;">${esc(rep.recommended_next_action || '')}</div>`;

  let sectionIndex = 0;
  function section(title, inner) {
    const div = document.createElement('div');
    div.className = 'report-section';
    div.style.animationDelay = (0.25 + sectionIndex * 0.12) + 's';
    sectionIndex++;
    div.innerHTML = `<div class="report-section-title">${esc(title)}</div>${inner}`;
    if (sheet && footer) sheet.insertBefore(div, footer); else sheet.appendChild(div);
  }

  // Key Clues (FACT / AI INFERENCE)
  if ((rep.key_clues || []).length) {
    section('Key Clues', `<ul class="report-list">${rep.key_clues.map(k => `
      <li><strong>${esc(k.clue_number)}</strong> ${esc(k.title)}${k.entity ? ' — ' + esc(k.entity) : ''}
        <span class="kind-tag kind-${k.kind === 'FACT' ? 'fact' : 'inference'}">${esc(k.kind)}</span>
        <span style="opacity:.6;">(${k.confidence}%)</span></li>`).join('')}</ul>`);
  }

  // Relationships (supported) — "Let Orion Solve It" tests every possible
  // pair of clues, which can produce many entries that all say the same
  // thing (e.g. five clues all pointing at one vendor). Group by the
  // underlying reason so the report reads as one clear line per finding
  // instead of one line per pair.
  if ((rep.relationships || []).length) {
    const groups = new Map();
    rep.relationships.forEach(r => {
      const reason = esc(r.basis || r.type || 'Related');
      if (!groups.has(reason)) groups.set(reason, new Set());
      const g = groups.get(reason);
      g.add(esc(r.from));
      g.add(esc(r.to));
    });
    const inner = `<ul class="report-list">${Array.from(groups.entries()).map(([reason, names]) =>
      `<li>${Array.from(names).join(' <span style="color:#7a1a1a;">•</span> ')}<br>
        <span style="font-size:13px;opacity:.7;">${reason}</span></li>`).join('')}</ul>`;
    section('Relationships', inner);
  }

  // Hypotheses
  if ((rep.hypotheses || []).length || (rep.rejected_hypotheses || []).length) {
    let inner = '<ul class="report-list">';
    (rep.hypotheses || []).forEach(h => inner += `<li>${esc(h.text)} <span class="kind-tag kind-inference">${esc(h.status)}</span></li>`);
    (rep.rejected_hypotheses || []).forEach(h => inner += `<li style="opacity:.7;">${esc(h.title)} <span class="kind-tag kind-decision">REJECTED</span><br><span style="font-size:13px;">${esc(h.reason)}</span></li>`);
    inner += '</ul>';
    section('Hypotheses — Supported & Rejected', inner);
  }

  // Investigation path
  if ((rep.investigation_path || []).length) {
    section('Investigation Path', `<ul class="report-list">${rep.investigation_path.map(s => `<li><strong>${esc(s.step)}</strong> — ${esc(s.content)}</li>`).join('')}</ul>`);
  }

  // Closing status — always the LAST thing on the report, in plain language.
  // COMPLETED cases confirm nothing is missing; UNFINISHED cases spell out
  // exactly what clues are still needed, so nothing is left half-open.
  const closing = document.createElement('div');
  closing.className = 'report-closing' + (rep.ready ? ' is-complete' : ' is-unfinished');
  closing.style.opacity = '0';
  closing.style.animation = `reportSectionIn 0.55s ease ${(0.25 + sectionIndex * 0.12 + 0.15)}s forwards`;
  if (rep.ready) {
    closing.innerHTML = `
      <div class="report-closing-title">✔ Case Status: COMPLETED</div>
      <div class="report-assessment">Every required connection has been made and no evidence is missing.
      This case is ready for final review.</div>`;
  } else {
    const missing = rep.missing_evidence || [];
    closing.innerHTML = `
      <div class="report-closing-title">⚠ Case Status: UNFINISHED</div>
      <div class="report-assessment" style="margin-bottom:8px;">
        This investigation is not yet complete. The following clue${missing.length === 1 ? ' is' : 's are'} still missing:
      </div>
      ${missing.length
        ? `<ul class="report-list">${missing.map(m => `<li>${esc(m)}</li>`).join('')}</ul>`
        : `<ul class="report-list"><li>More confirmed clues and at least one supported connection between them are still needed.</li></ul>`}`;
  }
  if (sheet && footer) sheet.insertBefore(closing, footer); else sheet.appendChild(closing);

  if (rep.ready) { setOrionState('alert'); orionSpeak('The case is documented.'); }
  else { orionSpeak('This report is unfinished — a few clues are still missing.'); }
}

/* ─── Router ───────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('create-investigation-screen')) initCreateInvestigation();
  else if (document.getElementById('evidence-intake-screen')) initEvidenceIntake();
  else if (document.getElementById('workspace-screen')) initWorkspace();
  else if (document.getElementById('report-screen')) initReport();
});

/* ═══════════════════════════════════════════════════════════════════
   Shared feature helpers (evidence preview, notebook, report extras)
═══════════════════════════════════════════════════════════════════ */
function escHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function escAttr(s) { return escHtml(s).replace(/"/g, '&quot;'); }

function closeModal() {
  const o = document.getElementById('noc-modal-overlay');
  if (o) { o.classList.remove('open'); setTimeout(() => o.remove(), 260); }
}

function showModal(title, sub, innerHTML) {
  closeModal();
  const overlay = document.createElement('div');
  overlay.id = 'noc-modal-overlay';
  overlay.className = 'noc-modal-overlay';
  overlay.innerHTML = `
    <div class="noc-modal">
      <div class="noc-modal-head">
        <div>
          <div class="noc-modal-title">${escHtml(title)}</div>
          <div class="noc-modal-sub">${sub || ''}</div>
        </div>
        <button class="noc-modal-close" aria-label="Close">×</button>
      </div>
      <div class="noc-modal-content">${innerHTML}</div>
    </div>`;
  document.body.appendChild(overlay);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(); });
  overlay.querySelector('.noc-modal-close').addEventListener('click', closeModal);
  requestAnimationFrame(() => overlay.classList.add('open'));
}

async function openEvidenceModal(invId, eid, name) {
  showModal(name, 'Loading exhibit…', '<div class="noc-preview-text">Opening…</div>');
  let d;
  try {
    const res = await fetch(`/api/investigations/${invId}/evidence/${eid}/preview`);
    d = await res.json();
  } catch (_) {
    showModal(name, 'error', '<div class="noc-preview-text">This exhibit could not be opened.</div>');
    return;
  }
  let body = '', sub = (d.type || '').toUpperCase();

  if (d.type === 'csv') {
    const dups = d.duplicates || [];
    sub = `${d.record_count} records · ${(d.columns || []).length} columns`
      + (dups.length ? ` · <span style="color:#7a1a1a;">duplicates: ${dups.map(escHtml).join(', ')}</span>` : '');
    const head = (d.columns || []).map(c => `<th>${escHtml(c)}</th>`).join('');
    const rows = (d.rows || []).map(r => {
      const tds = (d.columns || []).map(c => {
        const v = r[c] == null ? '' : r[c];
        const dup = dups.includes(String(v).trim());
        return `<td class="${dup ? 'noc-cell-dup' : ''}">${escHtml(v)}</td>`;
      }).join('');
      return `<tr>${tds}</tr>`;
    }).join('');
    body = `<div style="overflow:auto;"><table class="noc-table"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
    if (dups.length) body += `<div style="margin-top:10px;font-family:'Cormorant Garamond',serif;font-size:15px;color:#7a1a1a;">Highlighted cells repeat an identifier that should be unique — the duplicate-payment signal.</div>`;
  } else if (d.type === 'image') {
    body = `<img class="noc-preview-img" src="${escAttr(d.url)}" alt="${escAttr(name)}">`;
  } else if (d.type === 'pdf') {
    body = `<iframe src="${escAttr(d.url)}" style="width:100%;height:60vh;border:1px solid rgba(120,90,40,0.3);border-radius:4px;background:#fff;"></iframe>`;
  } else if (d.type === 'audio') {
    const peaks = d.peaks || [];
    const bars = peaks.map(p => `<span style="height:${Math.max(3, Math.round(p * 66))}px"></span>`).join('');
    body = `<div class="noc-wave">${bars}</div><audio controls src="${escAttr(d.url)}" style="width:100%;margin-top:10px;"></audio>`;
  } else {
    body = `<div class="noc-preview-text">${escHtml(d.text || '(empty document)')}</div>`;
  }
  showModal(name, sub, body);
}

/* ── Investigator's Diary — freeform notes + sticky notes on the board ── */
function buildNotebook(invId, canvasEl, stickyLayerEl) {
  if (document.getElementById('noc-notebook')) return;
  const nb = document.createElement('div');
  nb.id = 'noc-notebook';
  nb.className = 'noc-notebook';
  nb.innerHTML = `
    <div class="noc-notebook-head"><span>Investigator's Diary</span><span class="noc-nb-toggle">▲</span></div>
    <div class="noc-notebook-body">
      <textarea class="noc-note-input" rows="2" placeholder="Write anything — a hunch, a lead, a reminder…"></textarea>
      <button class="brass-button brass-button-sm noc-note-add" style="width:100%;margin-bottom:8px;">Save Entry</button>
      <input class="noc-note-search" placeholder="Search entries…">
      <div class="noc-note-list"><div class="noc-note-empty">No entries yet.</div></div>
    </div>`;
  document.body.appendChild(nb);

  const head = nb.querySelector('.noc-notebook-head');
  const input = nb.querySelector('.noc-note-input');
  const addBtn = nb.querySelector('.noc-note-add');
  const search = nb.querySelector('.noc-note-search');
  const list = nb.querySelector('.noc-note-list');
  let notes = [];
  let stickyOffset = 0;

  head.addEventListener('click', () => nb.classList.toggle('open'));

  function render(filter) {
    const q = (filter || '').toLowerCase();
    const shown = notes.filter(n => !q || n.body.toLowerCase().includes(q));
    list.innerHTML = shown.length
      ? shown.map(n => {
          let b = escHtml(n.body);
          if (q) b = b.replace(new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'ig'), '<em>$1</em>');
          return `
            <div class="noc-note" data-nid="${n.id}">
              <div class="noc-note-body">${b}</div>
              <div class="noc-note-actions">
                <button class="noc-note-act" data-act="edit" title="Edit">Edit</button>
                <button class="noc-note-act" data-act="pin" title="${n.pinned ? 'Remove from board' : 'Pin to board'}">${n.pinned ? 'Unpin' : 'Pin to Board'}</button>
                <button class="noc-note-act noc-note-del" data-act="delete" title="Delete">Delete</button>
              </div>
            </div>`;
        }).join('')
      : `<div class="noc-note-empty">${q ? 'No matching entries.' : 'No entries yet.'}</div>`;

    list.querySelectorAll('.noc-note').forEach(row => {
      const nid = Number(row.dataset.nid);
      row.querySelector('[data-act="edit"]').addEventListener('click', () => startEdit(row, nid));
      row.querySelector('[data-act="pin"]').addEventListener('click', () => togglePin(nid));
      row.querySelector('[data-act="delete"]').addEventListener('click', () => del(nid));
    });
  }

  function startEdit(row, nid) {
    const n = notes.find(x => x.id === nid);
    if (!n) return;
    row.innerHTML = `
      <textarea class="noc-note-edit-input" rows="2">${escHtml(n.body)}</textarea>
      <div class="noc-note-actions">
        <button class="noc-note-act" data-act="save">Save</button>
        <button class="noc-note-act" data-act="cancel">Cancel</button>
      </div>`;
    const ta = row.querySelector('textarea');
    ta.focus();
    row.querySelector('[data-act="cancel"]').addEventListener('click', () => render(search.value));
    row.querySelector('[data-act="save"]').addEventListener('click', async () => {
      const body = ta.value.trim();
      if (!body) return;
      try {
        const res = await fetch(`/api/notes/${nid}`, {
          method: 'PUT', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ body })
        });
        const updated = await res.json();
        notes = notes.map(x => x.id === nid ? updated : x);
      } catch (_) {}
      render(search.value);
      refreshSticky();
    });
  }

  async function togglePin(nid) {
    const n = notes.find(x => x.id === nid);
    if (!n) return;
    let payload = { pinned: !n.pinned };
    if (!n.pinned) {
      stickyOffset = (stickyOffset + 28) % 200;
      payload.x = 40 + stickyOffset;
      payload.y = 40 + stickyOffset;
    }
    try {
      const res = await fetch(`/api/notes/${nid}/pin`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const updated = await res.json();
      notes = notes.map(x => x.id === nid ? updated : x);
    } catch (_) {}
    render(search.value);
    refreshSticky();
  }

  async function del(nid) {
    try { await fetch(`/api/notes/${nid}`, { method: 'DELETE' }); } catch (_) {}
    notes = notes.filter(x => x.id !== nid);
    render(search.value);
    refreshSticky();
  }

  // ---- sticky notes on the board ----
  function refreshSticky() {
    if (!stickyLayerEl) return;
    const pinned = notes.filter(n => n.pinned);
    stickyLayerEl.innerHTML = '';
    pinned.forEach(n => {
      const el = document.createElement('div');
      el.className = 'sticky-note';
      el.style.left = (n.x != null ? n.x : 40) + 'px';
      el.style.top = (n.y != null ? n.y : 40) + 'px';
      el.dataset.nid = n.id;
      el.innerHTML = `
        <div class="sticky-note-body">${escHtml(n.body)}</div>
        <button class="sticky-note-close" title="Remove from board">×</button>`;
      stickyLayerEl.appendChild(el);

      el.querySelector('.sticky-note-close').addEventListener('click', async (e) => {
        e.stopPropagation();
        try {
          const res = await fetch(`/api/notes/${n.id}/pin`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pinned: false })
          });
          const updated = await res.json();
          notes = notes.map(x => x.id === n.id ? updated : x);
        } catch (_) {}
        render(search.value);
        refreshSticky();
      });

      el.addEventListener('pointerdown', (e) => {
        if (e.target.closest('.sticky-note-close')) return;
        e.preventDefault();
        const sx = e.clientX, sy = e.clientY;
        const ox = parseFloat(el.style.left), oy = parseFloat(el.style.top);
        try { el.setPointerCapture(e.pointerId); } catch (_) {}
        let nx = ox, ny = oy;
        const move = (ev) => {
          nx = ox + (ev.clientX - sx); ny = oy + (ev.clientY - sy);
          el.style.left = nx + 'px'; el.style.top = ny + 'px';
        };
        const up = async () => {
          el.removeEventListener('pointermove', move);
          el.removeEventListener('pointerup', up);
          try {
            await fetch(`/api/notes/${n.id}/pin`, {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ pinned: true, x: Math.round(nx), y: Math.round(ny) })
            });
          } catch (_) {}
        };
        el.addEventListener('pointermove', move);
        el.addEventListener('pointerup', up);
      });
    });
  }

  async function load() {
    try { notes = await (await fetch(`/api/investigations/${invId}/notes`)).json(); } catch { notes = []; }
    render(search.value);
    refreshSticky();
  }
  async function add() {
    const body = input.value.trim();
    if (!body) return;
    try {
      const res = await fetch(`/api/investigations/${invId}/notes`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ body })
      });
      const n = await res.json();
      notes.unshift(n); input.value = ''; render(search.value);
    } catch (_) {}
  }
  addBtn.addEventListener('click', add);
  search.addEventListener('input', () => render(search.value));
  load();
}
function openNotebook(open) {
  const nb = document.getElementById('noc-notebook');
  if (nb) nb.classList.toggle('open', open !== false);
}

/* ── Report extras: Challenge the Finding + real relationship graph ─ */
async function renderReportExtras(invId, report) {
  const sheet = document.querySelector('.report-sheet');
  const footer = sheet ? sheet.querySelector('.report-footer') : null;
  if (!sheet) return;
  const esc = escHtml;

  // Relationship map (real nodes)
  const rel = report.relationships || {};
  if (rel.nodes && rel.nodes.length) {
    const W = 460, H = 220, cx = W / 2, cy = H / 2, R = 88;
    const nodes = rel.nodes.slice(0, 16);
    const pos = {};
    nodes.forEach((n, i) => {
      const a = (i / nodes.length) * Math.PI * 2;
      pos[n.id] = { x: cx + Math.cos(a) * R, y: cy + Math.sin(a) * (R * 0.62) };
    });
    let g = '';
    (rel.edges || []).forEach(e => {
      const s = pos[e.source], t = pos[e.target];
      if (s && t) g += `<line x1="${s.x}" y1="${s.y}" x2="${t.x}" y2="${t.y}" stroke="rgba(122,26,26,0.25)" stroke-width="1"/>`;
    });
    const colors = { Vendor: '#7a1a1a', Invoice: '#8a6d2f', Account: '#a86b2a', Person: '#9a5a2a', Email: '#7a5a2a', Transaction: '#a85030' };
    nodes.forEach(n => {
      const p = pos[n.id];
      g += `<circle cx="${p.x}" cy="${p.y}" r="5" fill="${colors[n.type] || '#8a6d2f'}"/>`
        + `<text x="${p.x}" y="${p.y - 8}" font-size="9" text-anchor="middle" fill="#5a4a2e">${esc(String(n.label).slice(0, 12))}</text>`;
    });
    const sec = document.createElement('div');
    sec.className = 'report-section';
    sec.innerHTML = `<div class="report-section-title">Relationship Map</div>
      <svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}">${g}</svg>`;
    sheet.insertBefore(sec, footer);
  }

  // Challenge the Finding
  const sec = document.createElement('div');
  sec.className = 'report-section';
  sec.innerHTML = `<div class="report-section-title">Challenge the Finding</div>
    <button id="btn-challenge" class="brass-button brass-button-sm">Challenge This Finding</button>
    <div id="challenge-out"></div>`;
  sheet.insertBefore(sec, footer);

  document.getElementById('btn-challenge').addEventListener('click', async () => {
    const out = document.getElementById('challenge-out');
    out.innerHTML = '<div class="noc-preview-text" style="margin-top:10px;">Re-examining from the opposite view…</div>';
    let c;
    try { c = await (await fetch(`/api/investigations/${invId}/challenge`, { method: 'POST' })).json(); }
    catch { out.innerHTML = '<div class="noc-preview-text">Could not run the challenge.</div>'; return; }
    out.innerHTML = `
      <div class="noc-challenge">
        <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:16px;color:#4a3410;margin-bottom:8px;">${esc(c.counter_hypothesis)}</div>
        <div class="noc-challenge-cols">
          <div class="noc-for"><div class="noc-col-title">Evidence For</div><ul>${(c.evidence_for || []).map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>
          <div class="noc-against"><div class="noc-col-title">Evidence Against</div><ul>${(c.evidence_against || []).map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>
        </div>
        <div class="noc-conf-shift">Confidence <span class="noc-conf-old">${c.original_confidence}%</span> → <span class="noc-conf-new">${c.updated_confidence}%</span></div>
        <div style="font-family:'Cormorant Garamond',serif;font-size:15px;color:#7a1a1a;margin-top:6px;">${esc(c.verdict)}</div>
      </div>`;
    if (window.NOCTRAVoice) window.NOCTRAVoice.narrate('I have argued the other side. Confidence adjusted.');
  });
}
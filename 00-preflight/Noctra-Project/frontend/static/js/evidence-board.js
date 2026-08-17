/* ═══════════════════════════════════════════════════════════════════
   NOCTRA — Evidence Board (hub-level)
   Lists every case in the bureau. Clicking a case shows the evidence
   already linked to it — inline, on this same page. Opening a case here
   never begins a new investigation; "Begin Investigation" only happens
   from the New Case flow.
═══════════════════════════════════════════════════════════════════ */

import { createOrion, initOrionBehavior, orionSpeak } from './orion.js';

const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

document.addEventListener('DOMContentLoaded', () => {
  createOrion('orion-evidence-board');
  initOrionBehavior();

  const listEl = document.getElementById('eb-case-list');
  const detailEl = document.getElementById('eb-detail');
  const searchInput = document.getElementById('eb-search');

  let allCases = [];
  let selectedId = null;

  function caseRow(c) {
    const dateStr = c.created_at ? new Date(c.created_at).toLocaleDateString() : '';
    return `
      <button class="eb-case-row${c.id === selectedId ? ' active' : ''}" data-id="${c.id}">
        <span class="eb-case-row-name">${esc(c.case_name)}</span>
        <span class="eb-case-row-meta">${esc(c.case_number)} · ${dateStr}</span>
      </button>`;
  }

  function renderList() {
    const q = (searchInput.value || '').toLowerCase().trim();
    const items = allCases.filter(c => !q ||
      c.case_name.toLowerCase().includes(q) || c.case_number.toLowerCase().includes(q));
    listEl.innerHTML = items.length
      ? items.map(caseRow).join('')
      : '<div class="panel-empty">No cases match this search.</div>';
    listEl.querySelectorAll('.eb-case-row').forEach(btn => {
      btn.addEventListener('click', () => selectCase(Number(btn.dataset.id)));
    });
  }

  async function load() {
    let items = [];
    try { items = await (await fetch('/api/investigations')).json(); } catch (_) {}
    allCases = items;
    renderList();
    if (!allCases.length) {
      detailEl.innerHTML = `
        <div class="eb-detail-placeholder">
          <div class="eb-detail-placeholder-title">No cases yet</div>
          <div class="eb-detail-placeholder-sub">Nothing has been opened in this bureau yet.</div>
          <a href="/investigation/new" class="brass-button brass-button-sm" style="margin-top:14px;display:inline-block;">Begin an Investigation</a>
        </div>`;
    }
  }

  function fileIcon(type) {
    return { csv: '▤', pdf: '▥', image: '▧', audio: '♪' }[type] || '▦';
  }

  async function selectCase(id) {
    selectedId = id;
    renderList();
    const c = allCases.find(x => x.id === id);
    detailEl.innerHTML = '<div class="panel-empty">Loading evidence…</div>';

    let evidence = [], board = { clues: [], relationships: [], state: {} };
    try { evidence = await (await fetch(`/api/investigations/${id}/evidence`)).json(); } catch (_) {}
    try { board = await (await fetch(`/api/investigations/${id}/board`)).json(); } catch (_) {}

    const hasEvidence = evidence.length > 0;
    const hasBoard = (board.clues || []).length > 0;

    if (!hasEvidence && !hasBoard) {
      orionSpeak('Nothing has been filed for this case yet.');
      detailEl.innerHTML = `
        <div class="eb-detail-head">
          <div>
            <div class="eb-detail-title">${esc(c ? c.case_name : '')}</div>
            <div class="eb-detail-sub">${esc(c ? c.case_number : '')}</div>
          </div>
          <a class="brass-button brass-button-sm" href="/investigation/${id}/evidence">Add Evidence →</a>
        </div>
        <div class="eb-empty-case">
          <div class="eb-empty-case-title">This case has no evidence.</div>
          <div class="eb-empty-case-sub">Nothing has been uploaded or linked to this case's board yet. Add evidence to get started, or open the case to continue the investigation.</div>
          <a class="eb-open-link" href="/investigation/${id}">Open Investigation →</a>
        </div>`;
      return;
    }

    orionSpeak('Here is what has been linked to this case.');

    // Evidence exhibits
    const evidenceHtml = hasEvidence
      ? `<div class="eb-exhibit-grid">${evidence.map(e => `
          <div class="eb-exhibit">
            <span class="eb-exhibit-icon">${fileIcon(e.file_type)}</span>
            <span class="eb-exhibit-name">${esc(e.filename)}</span>
            <span class="eb-exhibit-type">${esc(e.file_type)}${e.analyzed ? '' : ' · not yet analyzed'}</span>
          </div>`).join('')}</div>`
      : `<div class="panel-empty">No raw evidence files uploaded yet.</div>`;

    // Linked evidence board (confirmed clues + supported connections)
    let boardHtml;
    if (hasBoard) {
      const clueMap = {};
      board.clues.forEach(cl => { clueMap[cl.id] = cl; });
      const tiles = board.clues.map(cl => `
        <div class="eb-clue-tile${cl.placed ? ' on-board' : ''}${(cl.confidence || 0) >= 75 ? ' is-main' : ''}">
          <div class="eb-clue-tile-num">${esc(cl.clue_number)}</div>
          <div class="eb-clue-tile-title">${esc(cl.title)}</div>
          <div class="eb-clue-tile-entity">${esc(cl.entity || '—')}</div>
          <div class="eb-clue-tile-conf">${cl.confidence}%</div>
        </div>`).join('');
      const rels = (board.relationships || []).filter(r => r.status === 'supported');
      const relHtml = rels.length
        ? `<div class="eb-rel-list">${rels.map(r => `
            <div class="eb-rel-row">
              <span>${esc((clueMap[r.source] || {}).title || '—')}</span>
              <span class="eb-rel-arrow">↔</span>
              <span>${esc((clueMap[r.target] || {}).title || '—')}</span>
              <span class="eb-rel-basis">${esc(r.basis || '')}</span>
            </div>`).join('')}</div>`
        : `<div class="panel-empty">No supported connections between clues yet.</div>`;
      boardHtml = `
        <div class="eb-clue-grid">${tiles}</div>
        <div class="eb-section-subtitle">Linked Connections</div>
        ${relHtml}`;
    } else {
      boardHtml = `<div class="panel-empty">Evidence has been uploaded but no clues have been confirmed onto this case's board yet.</div>`;
    }

    const state = board.state || {};
    const conf = state.confidence || 0;

    detailEl.innerHTML = `
      <div class="eb-detail-head">
        <div>
          <div class="eb-detail-title">${esc(c ? c.case_name : (board.case_name || ''))}</div>
          <div class="eb-detail-sub">${esc(c ? c.case_number : '')} · Case confidence ${conf}%</div>
        </div>
        <a class="brass-button brass-button-sm" href="/investigation/${id}">Open Full Board →</a>
      </div>
      <div class="eb-section-subtitle">Evidence Exhibits</div>
      ${evidenceHtml}
      <div class="eb-section-subtitle">Evidence Board (linked clues)</div>
      ${boardHtml}`;
  }

  searchInput.addEventListener('input', renderList);
  load();
});

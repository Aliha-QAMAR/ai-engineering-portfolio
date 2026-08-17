/* ═══════════════════════════════════════════════════════════════════
   NOCTRA — Screen 8: Case Archive
   Wooden drawers grouped into Active · Solved · Featured · Closed,
   each sliding open. Featured = the seeded investigation library.
═══════════════════════════════════════════════════════════════════ */

import { createOrion, initOrionBehavior, orionSpeak } from './orion.js';

document.addEventListener('DOMContentLoaded', () => {
  createOrion('orion-archive');
  initOrionBehavior();

  const container = document.getElementById('archive-drawers');
  const searchInput = document.getElementById('archive-search');
  const filters = document.querySelectorAll('.filter-chip');

  let allCases = [];
  let activeFilter = 'all';

  const isFeatured = (c) => (c.case_number || '').startsWith('NOC-CASE-');
  function bucketOf(c) {
    if (c.status === 'deleted') return 'deleted';
    if (isFeatured(c)) return 'featured';
    if (c.status === 'solved' || c.status === 'complete') return 'solved';
    if (c.status === 'closed') return 'closed';
    return 'active';
  }

  const SECTIONS = [
    { key: 'active', label: 'Active Cases' },
    { key: 'solved', label: 'Solved Cases' },
    { key: 'featured', label: 'Featured Investigations' },
    { key: 'closed', label: 'Closed Cases' },
    { key: 'deleted', label: 'Removed' },
  ];

  function caseRow(c) {
    const b = bucketOf(c);
    const dateStr = c.created_at ? new Date(c.created_at).toLocaleDateString() : '';
    const tag = isFeatured(c) ? 'FEATURED' : b.toUpperCase();
    return `
      <div class="drawer drawer-row" data-id="${c.id}">
        <div class="drawer-row-main">
          <div class="drawer-case-name">${c.case_name}</div>
          <div class="drawer-case-meta">${c.case_number} · ${dateStr} · ${tag}</div>
        </div>
        <div class="drawer-actions">
          ${b === 'deleted'
            ? `<button class="drawer-btn restore-btn" data-id="${c.id}">Restore</button>`
            : `<a class="drawer-btn" href="/investigation/${c.id}">Open</a>
               <a class="drawer-btn" href="/investigation/${c.id}/report">Report</a>
               ${isFeatured(c) ? '' : `<button class="drawer-btn danger delete-btn" data-id="${c.id}">Delete</button>`}`}
        </div>
      </div>`;
  }

  function render() {
    const q = (searchInput.value || '').toLowerCase().trim();
    let list = allCases.filter(c =>
      !q || c.case_name.toLowerCase().includes(q) || c.case_number.toLowerCase().includes(q));

    const visibleSections = SECTIONS.filter(s => activeFilter === 'all' || activeFilter === s.key);
    let html = '';
    let total = 0;
    for (const sec of visibleSections) {
      const items = list.filter(c => bucketOf(c) === sec.key);
      if (!items.length && activeFilter === 'all' && sec.key === 'deleted') continue;
      if (!items.length && activeFilter === 'all' && sec.key === 'closed') continue;
      total += items.length;
      html += `
        <div class="noc-drawer-section" data-section="${sec.key}">
          <div class="noc-drawer-section-head"><span>${sec.label}</span><span>${items.length} ▾</span></div>
          <div class="noc-drawer-section-body" style="max-height:2000px;">
            ${items.length ? items.map(caseRow).join('')
              : '<div class="panel-empty" style="padding:8px 0;">No cases in this drawer.</div>'}
          </div>
        </div>`;
    }
    container.innerHTML = total || html ? html : '<div class="panel-empty">No cases match this search.</div>';

    // drawer slide open/close
    container.querySelectorAll('.noc-drawer-section-head').forEach(head => {
      head.addEventListener('click', () => {
        const sec = head.closest('.noc-drawer-section');
        const body = sec.querySelector('.noc-drawer-section-body');
        const collapsed = sec.classList.toggle('collapsed');
        body.style.maxHeight = collapsed ? '0' : '2000px';
      });
    });

    container.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        await fetch(`/api/investigations/${btn.dataset.id}`, { method: 'DELETE' });
        orionSpeak('Filed away. Nothing is ever truly gone from this bureau.');
        load();
      });
    });
    container.querySelectorAll('.restore-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        await fetch(`/api/investigations/${btn.dataset.id}/restore`, { method: 'POST' });
        orionSpeak('The case returns to the light.');
        load();
      });
    });
  }

  async function load() {
    const res = await fetch('/api/investigations?include_deleted=1');
    allCases = await res.json();
    render();
  }

  searchInput.addEventListener('input', render);
  filters.forEach(chip => {
    chip.addEventListener('click', () => {
      filters.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      activeFilter = chip.dataset.filter;
      render();
    });
  });

  load();
});

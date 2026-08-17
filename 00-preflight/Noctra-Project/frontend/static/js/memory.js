/* ═══════════════════════════════════════════════════════════════════
   NOCTRA — Screen 9: Memory Vault
   Connected to AI long-term memory. Shows recovered discoveries,
   related investigations, and a similarity percentage between them.
═══════════════════════════════════════════════════════════════════ */

import { createOrion, initOrionBehavior, orionSpeak } from './orion.js';

const STOP = new Set(['this','that','with','from','case','closed','investigated','duplicate','found','were','have','been','into','across','more','than','once']);
function tokens(s) {
  return new Set(String(s || '').toLowerCase().match(/[a-z]{4,}/g)?.filter(w => !STOP.has(w)) || []);
}
function similarity(a, b) {
  const A = tokens(a), B = tokens(b);
  if (!A.size || !B.size) return 0;
  let inter = 0; A.forEach(w => { if (B.has(w)) inter++; });
  return Math.round(inter / new Set([...A, ...B]).size * 100);
}

document.addEventListener('DOMContentLoaded', async () => {
  createOrion('orion-memory');
  initOrionBehavior();

  const vault = document.getElementById('memory-vault');

  let memories = [];
  try {
    memories = await (await fetch('/api/memory')).json();
  } catch (_) {
    vault.innerHTML = '<div class="panel-empty">The vault could not be reached. Try again shortly.</div>';
    return;
  }
  if (!memories.length) return; // keep the default "vault is quiet" message

  // reference = most recent recollection; score the rest against it
  const ref = memories[0];
  const text = (m) => `${m.key} ${m.value}`;

  vault.innerHTML = memories.map((m, i) => {
    const dateStr = m.created_at ? new Date(m.created_at).toLocaleDateString() : '';
    const sim = i === 0 ? null : similarity(text(ref), text(m));
    const simBlock = (sim != null) ? `
      <span class="mc-similarity">${sim}% match</span>
      <div class="mc-sim-bar"><div class="mc-sim-fill" style="width:${sim}%"></div></div>` : '';
    const caseLink = m.investigation_id
      ? `<a href="/investigation/${m.investigation_id}/report" style="color:#c9a84c;font-size:11px;">View related case →</a>` : '';
    return `
      <div class="memory-card">
        <div class="mc-key">${(m.key || 'Untitled Recollection')}${simBlock ? '' : ''}</div>
        ${simBlock}
        <div class="mc-value">${m.value || ''}</div>
        <div class="mc-date">${dateStr} ${caseLink}</div>
      </div>`;
  }).join('');

  const related = memories.slice(1).map((m, i) => ({ m, sim: similarity(text(ref), text(m)) }))
    .filter(x => x.sim >= 40).sort((a, b) => b.sim - a.sim)[0];
  if (related) {
    orionSpeak(`This resembles ${related.m.key} — ${related.sim}% alike.`);
  }
});

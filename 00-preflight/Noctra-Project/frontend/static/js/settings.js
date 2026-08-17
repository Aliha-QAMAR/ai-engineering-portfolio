/* ═══════════════════════════════════════════════════════════════════
   NOCTRA — Screen 10: Settings
═══════════════════════════════════════════════════════════════════ */

import { createOrion, initOrionBehavior, orionSpeak } from './orion.js';
import './sound.js';

const PREF_KEY = 'noctra-preferences';

function loadPrefs() {
  try { return JSON.parse(localStorage.getItem(PREF_KEY)) || {}; }
  catch { return {}; }
}
function savePrefs(prefs) {
  localStorage.setItem(PREF_KEY, JSON.stringify(prefs));
}

document.addEventListener('DOMContentLoaded', async () => {
  createOrion('orion-settings');
  initOrionBehavior();

  const codenameEl = document.getElementById('settings-codename');
  const clearanceEl = document.getElementById('settings-clearance');
  const motionToggle = document.getElementById('toggle-reduced-motion');
  const lampToggle = document.getElementById('toggle-lamp-alerts');
  const orionToggle = document.getElementById('toggle-orion-remarks');
  const logoutBtn = document.getElementById('btn-settings-logout');

  try {
    const res = await fetch('/api/auth/status');
    const data = await res.json();
    if (data.authenticated) {
      codenameEl.textContent = data.codename;
      clearanceEl.textContent = (data.clearance_level || 'alpha').toUpperCase();
    } else {
      codenameEl.textContent = 'Not signed in';
      clearanceEl.textContent = '—';
    }
  } catch {
    codenameEl.textContent = 'Unavailable';
  }

  const prefs = loadPrefs();
  motionToggle.checked = !!prefs.reducedMotion;
  lampToggle.checked = prefs.lampAlerts !== false;
  orionToggle.checked = prefs.orionRemarks !== false;

  if (motionToggle.checked) document.body.classList.add('reduced-motion');

  motionToggle.addEventListener('change', () => {
    const p = loadPrefs();
    p.reducedMotion = motionToggle.checked;
    savePrefs(p);
    document.body.classList.toggle('reduced-motion', motionToggle.checked);
  });
  lampToggle.addEventListener('change', () => {
    const p = loadPrefs();
    p.lampAlerts = lampToggle.checked;
    savePrefs(p);
  });
  orionToggle.addEventListener('change', () => {
    const p = loadPrefs();
    p.orionRemarks = orionToggle.checked;
    savePrefs(p);
    if (orionToggle.checked) orionSpeak('I shall speak up when it matters.');
  });

  // ── New feature preferences ──────────────────────────────────────
  const ambientToggle = document.getElementById('toggle-ambient');
  const narrationToggle = document.getElementById('toggle-narration');
  const voiceSelect = document.getElementById('pref-voice');
  const modeSelect = document.getElementById('pref-mode');

  if (ambientToggle) {
    ambientToggle.checked = prefs.ambientSound === true;
    ambientToggle.addEventListener('change', () => {
      const p = loadPrefs(); p.ambientSound = ambientToggle.checked; savePrefs(p);
      if (window.NOCTRAAmbient) { ambientToggle.checked ? window.NOCTRAAmbient.start() : window.NOCTRAAmbient.stop(); }
    });
  }
  if (narrationToggle) {
    narrationToggle.checked = prefs.voiceMuted !== true;
    narrationToggle.addEventListener('change', () => {
      const p = loadPrefs(); p.voiceMuted = !narrationToggle.checked; savePrefs(p);
      if (window.NOCTRAVoice) window.NOCTRAVoice.setMuted(!narrationToggle.checked);
      if (narrationToggle.checked) orionSpeak('Narration on. I will speak the important moments.');
    });
  }
  if (voiceSelect) {
    voiceSelect.value = prefs.voiceName || 'onyx';
    voiceSelect.addEventListener('change', () => {
      const p = loadPrefs(); p.voiceName = voiceSelect.value; savePrefs(p);
      if (window.NOCTRAVoice) window.NOCTRAVoice.narrate('This is my voice.');
    });
  }
  if (modeSelect) {
    modeSelect.value = prefs.defaultMode || 'autonomous';
    modeSelect.addEventListener('change', () => {
      const p = loadPrefs(); p.defaultMode = modeSelect.value; savePrefs(p);
    });
  }

  logoutBtn.addEventListener('click', async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/';
  });
});

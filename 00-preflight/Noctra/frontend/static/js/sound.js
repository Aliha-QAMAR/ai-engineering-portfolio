/* ═══════════════════════════════════════════════════════════════════
   NOCTRA — Ambient Sound (synthesised, no audio files)
   Subtle rain + occasional clock tick via Web Audio. Muted by default;
   toggled from Settings. Requires a user gesture to begin (browser rule).
═══════════════════════════════════════════════════════════════════ */
const PREF_KEY = 'noctra-preferences';
function prefs() { try { return JSON.parse(localStorage.getItem(PREF_KEY) || '{}'); } catch { return {}; } }
function savePrefs(p) { localStorage.setItem(PREF_KEY, JSON.stringify(p)); }

let ctx = null, rainGain = null, tickTimer = null, running = false;

function build() {
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return false;
  ctx = new AC();
  // rain = filtered white noise
  const bufferSize = 2 * ctx.sampleRate;
  const noise = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const out = noise.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) out[i] = Math.random() * 2 - 1;
  const src = ctx.createBufferSource(); src.buffer = noise; src.loop = true;
  const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 1100;
  const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 400;
  rainGain = ctx.createGain(); rainGain.gain.value = 0.05;
  src.connect(hp); hp.connect(lp); lp.connect(rainGain); rainGain.connect(ctx.destination);
  src.start(0);
  return true;
}

function tick() {
  if (!ctx || !running) return;
  const o = ctx.createOscillator(), g = ctx.createGain();
  o.type = 'sine'; o.frequency.value = 1600;
  g.gain.setValueAtTime(0.0009, ctx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + 0.05);
  o.connect(g); g.connect(ctx.destination); o.start(); o.stop(ctx.currentTime + 0.06);
  tickTimer = setTimeout(tick, 1000);
}

function start() {
  if (running) return;
  if (!ctx && !build()) return;
  if (ctx.state === 'suspended') ctx.resume();
  running = true; tick();
  const p = prefs(); p.ambientSound = true; savePrefs(p);
}
function stop() {
  running = false; clearTimeout(tickTimer);
  if (rainGain) rainGain.gain.value = 0;
  const p = prefs(); p.ambientSound = false; savePrefs(p);
}
function toggle() { running ? stop() : start(); return running; }

// auto-start on first gesture if the user previously enabled it
function armAutostart() {
  if (prefs().ambientSound !== true) return;
  const go = () => { start(); window.removeEventListener('pointerdown', go); };
  window.addEventListener('pointerdown', go, { once: true });
}
armAutostart();

window.NOCTRAAmbient = { start, stop, toggle, isOn: () => running };
export { start, stop, toggle };

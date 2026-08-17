/* ═══════════════════════════════════════════════════════════════════
   NOCTRA — AI Voice Investigator
   • Brass microphone → speech recognition (Web Speech API)
   • AI speaks back via OpenAI TTS (/api/tts), falling back to the
     browser's speech synthesis when no key is configured.
   • Narration can be muted at any time.
═══════════════════════════════════════════════════════════════════ */

const PREF_KEY = 'noctra-preferences';
function prefs() { try { return JSON.parse(localStorage.getItem(PREF_KEY) || '{}'); } catch { return {}; } }
function savePrefs(p) { localStorage.setItem(PREF_KEY, JSON.stringify(p)); }

let audioEl = null;
let muted = prefs().voiceMuted === true;

function browserSpeak(text) {
  if (!('speechSynthesis' in window)) return;
  try {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.98; u.pitch = 0.9;
    const want = prefs().voiceName;
    const voices = window.speechSynthesis.getVoices();
    const pick = voices.find(v => v.name === want)
      || voices.find(v => /onyx|daniel|male|en-GB/i.test(v.name))
      || voices[0];
    if (pick) u.voice = pick;
    window.speechSynthesis.speak(u);
  } catch (_) {}
}

async function narrate(text) {
  if (muted || !text) return;
  const caption = document.getElementById('noc-voice-caption');
  if (caption) { caption.textContent = '“' + text + '”'; caption.style.display = 'block';
    clearTimeout(caption._t); caption._t = setTimeout(() => caption.style.display = 'none', 4200); }
  try {
    const res = await fetch('/api/tts', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice: prefs().voiceName || 'onyx' })
    });
    if (res.status === 204 || !res.ok) { browserSpeak(text); return; }
    const blob = await res.blob();
    if (!blob || blob.size < 200) { browserSpeak(text); return; }
    if (!audioEl) audioEl = new Audio();
    audioEl.src = URL.createObjectURL(blob);
    audioEl.play().catch(() => browserSpeak(text));
  } catch (_) { browserSpeak(text); }
}

function setMuted(v) {
  muted = v; const p = prefs(); p.voiceMuted = v; savePrefs(p);
  if (v && audioEl) audioEl.pause();
  if (v && 'speechSynthesis' in window) window.speechSynthesis.cancel();
  const btn = document.getElementById('noc-mic-mute');
  if (btn) btn.textContent = v ? '🔇' : '🔊';
}

const MIC_SVG = `<svg viewBox="0 0 24 24" fill="none">
  <rect x="9" y="2" width="6" height="12" rx="3" fill="#2a1c08"/>
  <path d="M5 11a7 7 0 0 0 14 0" stroke="#2a1c08" stroke-width="1.6" fill="none"/>
  <line x1="12" y1="18" x2="12" y2="22" stroke="#2a1c08" stroke-width="1.6"/>
  <line x1="8" y1="22" x2="16" y2="22" stroke="#2a1c08" stroke-width="1.6"/></svg>`;

/* Build the brass mic, mute control and wire speech recognition. */
export function initVoiceInvestigator({ onCommand } = {}) {
  if (document.getElementById('noc-mic')) return;

  const caption = document.createElement('div');
  caption.id = 'noc-voice-caption'; caption.className = 'noc-voice-caption';
  document.body.appendChild(caption);

  const mute = document.createElement('div');
  mute.id = 'noc-mic-mute'; mute.className = 'noc-mic-mute';
  mute.title = 'Mute narration'; mute.textContent = muted ? '🔇' : '🔊';
  mute.addEventListener('click', () => setMuted(!muted));
  document.body.appendChild(mute);

  const mic = document.createElement('div');
  mic.id = 'noc-mic'; mic.className = 'noc-mic';
  mic.title = 'Voice Mode — click and speak a command';
  mic.innerHTML = MIC_SVG;
  document.body.appendChild(mic);

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  let rec = null, listening = false;
  if (SR) {
    rec = new SR();
    rec.lang = 'en-US'; rec.interimResults = false; rec.maxAlternatives = 1;
    rec.onresult = (e) => {
      const transcript = e.results[0][0].transcript.trim();
      caption.textContent = '❝ ' + transcript + ' ❞'; caption.style.display = 'block';
      if (typeof onCommand === 'function') onCommand(transcript);
    };
    rec.onend = () => { listening = false; mic.classList.remove('listening'); };
    rec.onerror = () => { listening = false; mic.classList.remove('listening'); };
  }

  mic.addEventListener('click', () => {
    if (!rec) {
      narrate('Voice recognition is not supported in this browser, but I can still speak.');
      return;
    }
    if (listening) { rec.stop(); return; }
    try { rec.start(); listening = true; mic.classList.add('listening'); } catch (_) {}
  });

  // warm up voices list for the fallback
  if ('speechSynthesis' in window) window.speechSynthesis.getVoices();
}

// expose to non-module callers (orion.js narrates through this)
window.NOCTRAVoice = { narrate, speak: narrate, setMuted, isMuted: () => muted };
export { narrate, setMuted };

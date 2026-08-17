// Orion — NOCTRA's Detective Owl Companion
// SVG geometry is LOCKED — never change colors, proportions, or features

const CLAMP = (min, max, val) => Math.max(min, Math.min(max, val));

// The Orion container currently on screen — used to anchor his speech bubble.
let activeOrionSlot = null;
let orionSpeechTimer = null;

export function createOrion(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  activeOrionSlot = container;

  container.innerHTML = `
    <svg viewBox="-90 -180 180 220" width="180" height="220" style="overflow: visible; filter: drop-shadow(0 8px 30px rgba(0,0,0,0.8));">
      <defs>
        <radialGradient id="bodyGrd" cx="40%" cy="30%">
          <stop offset="0%" stop-color="#5c3d20"/>
          <stop offset="45%" stop-color="#3a2510"/>
          <stop offset="100%" stop-color="#1e1208"/>
        </radialGradient>
        <radialGradient id="bellyGrd" cx="50%" cy="40%">
          <stop offset="0%" stop-color="#7a5a30"/>
          <stop offset="60%" stop-color="#5a4020"/>
          <stop offset="100%" stop-color="#3a2810"/>
        </radialGradient>
        <radialGradient id="irisGrd" cx="35%" cy="30%">
          <stop offset="0%" stop-color="#f5b800"/>
          <stop offset="40%" stop-color="#d48000"/>
          <stop offset="80%" stop-color="#a85000"/>
          <stop offset="100%" stop-color="#6a2800"/>
        </radialGradient>
        <radialGradient id="headGrd" cx="35%" cy="25%">
          <stop offset="0%" stop-color="#503820"/>
          <stop offset="60%" stop-color="#2e1e0c"/>
          <stop offset="100%" stop-color="#1a1008"/>
        </radialGradient>
        <linearGradient id="wingGrd" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#3a2510"/>
          <stop offset="100%" stop-color="#1e1208"/>
        </linearGradient>
      </defs>

      <!-- Talons -->
      <g style="transform: translateY(28px);">
        <path d="M -30 30 Q -35 38 -42 32" stroke="#1a1008" stroke-width="4" stroke-linecap="round" fill="none"/>
        <path d="M -30 30 Q -28 40 -22 36" stroke="#1a1008" stroke-width="4" stroke-linecap="round" fill="none"/>
        <path d="M -30 30 Q -20 38 -16 32" stroke="#1a1008" stroke-width="3.5" stroke-linecap="round" fill="none"/>
        <circle cx="-30" cy="30" r="5" fill="#1e1208"/>
        <path d="M 30 30 Q 35 38 42 32" stroke="#1a1008" stroke-width="4" stroke-linecap="round" fill="none"/>
        <path d="M 30 30 Q 28 40 22 36" stroke="#1a1008" stroke-width="4" stroke-linecap="round" fill="none"/>
        <path d="M 30 30 Q 20 38 16 32" stroke="#1a1008" stroke-width="3.5" stroke-linecap="round" fill="none"/>
        <circle cx="30" cy="30" r="5" fill="#1e1208"/>
      </g>

      <!-- Body -->
      <g class="owl-body-anim">
        <ellipse cx="0" cy="10" rx="62" ry="78" fill="url(#bodyGrd)"/>
        <path d="M -62 -10 C -70 10, -68 40, -58 65 C -52 78, -42 82, -30 70 C -20 60, -15 40, -18 10 Z" fill="url(#wingGrd)" class="owl-wing-anim"/>
        <path d="M -62 10 C -65 30, -55 55, -40 70" stroke="rgba(0,0,0,0.35)" stroke-width="1.5" fill="none"/>
        <path d="M -64 30 C -66 45, -55 65, -37 70" stroke="rgba(0,0,0,0.35)" stroke-width="1.5" fill="none"/>
        <path d="M -60 -10 C -64 15, -55 45, -43 70" stroke="rgba(0,0,0,0.35)" stroke-width="1.5" fill="none"/>
        
        <path d="M 62 -10 C 70 10, 68 40, 58 65 C 52 78, 42 82, 30 70 C 20 60, 15 40, 18 10 Z" fill="url(#wingGrd)" class="owl-wing-anim"/>
        <path d="M 60 30 C 64 45, 55 65, 37 70" stroke="rgba(0,0,0,0.35)" stroke-width="1.5" fill="none"/>
        <path d="M 62 10 C 65 30, 55 55, 40 70" stroke="rgba(0,0,0,0.35)" stroke-width="1.5" fill="none"/>
        <path d="M 64 -10 C 66 15, 55 45, 43 70" stroke="rgba(0,0,0,0.35)" stroke-width="1.5" fill="none"/>

        <ellipse cx="0" cy="18" rx="38" ry="58" fill="url(#bellyGrd)"/>
        <!-- feathers -->
        <path d="M -23 -44 Q -18 -34, -13 -39" stroke="rgba(0,0,0,0.3)" stroke-width="1.2" stroke-linecap="round" fill="none"/>
        <path d="M -14 -36 Q -9 -26, -4 -31" stroke="rgba(0,0,0,0.3)" stroke-width="1.2" stroke-linecap="round" fill="none"/>
        <path d="M -5 -28 Q 0 -18, 5 -23" stroke="rgba(0,0,0,0.3)" stroke-width="1.2" stroke-linecap="round" fill="none"/>
        <path d="M 4 -20 Q 9 -10, 14 -15" stroke="rgba(0,0,0,0.3)" stroke-width="1.2" stroke-linecap="round" fill="none"/>
        <path d="M 13 -12 Q 18 -2, 23 -7" stroke="rgba(0,0,0,0.3)" stroke-width="1.2" stroke-linecap="round" fill="none"/>
      </g>

      <!-- Head -->
      <g id="orionHead" style="transform-origin: 0px -40px; transition: transform 0.6s cubic-bezier(0.4,0,0.2,1);">
        <circle cx="0" cy="-72" r="52" fill="url(#headGrd)"/>
        <polygon points="-28,-122 -22,-95 -10,-118" fill="#1e1208"/>
        <polygon points="-26,-122 -20,-96 -9,-116" fill="#2e1e0c"/>
        <polygon points="28,-122 22,-95 10,-118" fill="#1e1208"/>
        <polygon points="26,-122 20,-96 9,-116" fill="#2e1e0c"/>
        <ellipse cx="0" cy="-68" rx="36" ry="42" fill="#4a3018" opacity="0.7"/>

        <!-- Left eye -->
        <circle cx="-20" cy="-70" r="17" fill="#0a0502"/>
        <circle cx="-20" cy="-70" r="15" fill="url(#irisGrd)"/>
        <circle id="orionEyeL" cx="-20" cy="-70" r="8" fill="#050200"/>
        <circle id="orionHighlightL" cx="-23" cy="-73" r="2.5" fill="rgba(255,248,220,0.75)"/>
        <clipPath id="lec"><circle cx="-20" cy="-70" r="17"/></clipPath>
        <rect id="orionEyelidL" x="-38" y="-107" width="36" height="22" fill="#2e1e0c" clip-path="url(#lec)" style="transition: y 0.08s ease;"/>

        <!-- Right eye -->
        <circle cx="20" cy="-70" r="17" fill="#0a0502"/>
        <circle cx="20" cy="-70" r="15" fill="url(#irisGrd)"/>
        <circle id="orionEyeR" cx="20" cy="-70" r="8" fill="#050200"/>
        <circle id="orionHighlightR" cx="23" cy="-73" r="2.5" fill="rgba(255,248,220,0.75)"/>
        <clipPath id="rec"><circle cx="20" cy="-70" r="17"/></clipPath>
        <rect id="orionEyelidR" x="2" y="-107" width="36" height="22" fill="#2e1e0c" clip-path="url(#rec)" style="transition: y 0.08s ease;"/>

        <path d="M -7 -58 L 0 -44 L 7 -58 Q 0 -62 -7 -58 Z" fill="#9a8040"/>
      </g>
    </svg>
    <div id="orionSpeech" class="orion-speech"></div>
  `;
}

export function initOrionBehavior() {
  const head = document.getElementById('orionHead');
  const eyeL = document.getElementById('orionEyeL');
  const eyeR = document.getElementById('orionEyeR');
  const highL = document.getElementById('orionHighlightL');
  const highR = document.getElementById('orionHighlightR');
  const lidL = document.getElementById('orionEyelidL');
  const lidR = document.getElementById('orionEyelidR');

  if (!head) return;

  const onMove = (e) => {
    const rect = head.getBoundingClientRect();
    const owlCenterX = rect.left + rect.width / 2;
    const owlCenterY = rect.top + rect.height / 2;
    const dx = e.clientX - owlCenterX;
    const dy = e.clientY - owlCenterY;
    const dist = Math.sqrt(dx*dx + dy*dy) || 1;
    const angle = Math.atan2(dx, -dy) * (180/Math.PI);
    
    const headAngle = CLAMP(-15, 15, angle * 0.4);
    head.style.transform = `rotate(${headAngle}deg)`;

    const f = Math.min(1, dist/400);
    const eyeOffsetX = (dx/dist)*4*f;
    const eyeOffsetY = (dy/dist)*4*f;

    if (eyeL) {
      eyeL.setAttribute('cx', -20 + eyeOffsetX);
      eyeL.setAttribute('cy', -70 + eyeOffsetY);
      highL.setAttribute('cx', -20 + eyeOffsetX - 3);
      highL.setAttribute('cy', -70 + eyeOffsetY - 3);
    }
    if (eyeR) {
      eyeR.setAttribute('cx', 20 + eyeOffsetX);
      eyeR.setAttribute('cy', -70 + eyeOffsetY);
      highR.setAttribute('cx', 20 + eyeOffsetX + 3);
      highR.setAttribute('cy', -70 + eyeOffsetY - 3);
    }
  };

  window.addEventListener('mousemove', onMove);

  const blink = () => {
    if (lidL) lidL.setAttribute('y', '-87');
    if (lidR) lidR.setAttribute('y', '-87');
    
    setTimeout(() => {
      if (lidL) lidL.setAttribute('y', '-107');
      if (lidR) lidR.setAttribute('y', '-107');
      
      if (Math.random() < 0.25) {
        setTimeout(() => {
          if (lidL) lidL.setAttribute('y', '-87');
          if (lidR) lidR.setAttribute('y', '-87');
          setTimeout(() => {
            if (lidL) lidL.setAttribute('y', '-107');
            if (lidR) lidR.setAttribute('y', '-107');
          }, 120);
        }, 200);
      }
    }, 120);
    
    setTimeout(blink, 2500 + Math.random()*5000);
  };
  
  setTimeout(blink, 2500 + Math.random()*3000);
}

export function moveOrionTo(x, y, duration) {
  // Logic for smoothly repositioning Orion
}

/* Position the subtitle bubble directly above Orion's head (not the screen top). */
function positionSpeech(bubble) {
  const slot = activeOrionSlot
    || document.querySelector('.orion-slot')
    || document.getElementById('orion-container');
  if (!slot) return;
  const svg = slot.querySelector('svg');
  const rect = (svg || slot).getBoundingClientRect();
  bubble.style.position = 'fixed';
  bubble.style.visibility = 'hidden';
  bubble.style.display = 'block';
  const bw = bubble.offsetWidth || 160;
  const bh = bubble.offsetHeight || 36;
  // centre horizontally over Orion; sit just above his head with the tail pointing down
  let left = rect.left + rect.width / 2 - bw / 2;
  left = Math.max(12, Math.min(window.innerWidth - bw - 12, left));
  let top = rect.top - bh - 14;
  if (top < 12) top = rect.bottom + 14; // if no room above, drop below
  bubble.style.left = `${left}px`;
  bubble.style.top = `${top}px`;
  // move the tail under Orion's centre
  const tailX = CLAMP(10, bw - 20, rect.left + rect.width / 2 - left - 6);
  bubble.style.setProperty('--tail-x', `${tailX}px`);
  bubble.style.visibility = 'visible';
}

export function orionSpeak(text) {
  // respect the "Orion's Remarks" preference
  try {
    const prefs = JSON.parse(localStorage.getItem('noctra-preferences') || '{}');
    if (prefs.orionRemarks === false) return;
  } catch (_) {}

  const bubble = document.getElementById('orion-speech');
  if (!bubble) return;
  clearTimeout(orionSpeechTimer);
  bubble.textContent = text;
  bubble.classList.add('orion-speech-anchored');
  positionSpeech(bubble);
  requestAnimationFrame(() => {
    bubble.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    bubble.style.opacity = '1';
    bubble.style.transform = 'translateY(0)';
  });
  // speak aloud too, if the voice layer is active and unmuted
  if (window.NOCTRAVoice && typeof window.NOCTRAVoice.narrate === 'function') {
    window.NOCTRAVoice.narrate(text);
  }
  orionSpeechTimer = setTimeout(() => {
    bubble.style.opacity = '0';
    bubble.style.transform = 'translateY(6px)';
    setTimeout(() => { bubble.style.display = 'none'; }, 400);
  }, 3600);
}

/* A brief "leaning in" gesture — Orion zooms toward the evidence, then settles. */
export function orionLeanIn() {
  const slot = activeOrionSlot;
  if (!slot) return;
  const svg = slot.querySelector('svg');
  if (!svg) return;
  svg.style.transition = 'transform 0.5s cubic-bezier(0.4,0,0.2,1)';
  svg.style.transform = 'scale(1.16) translateY(-8px)';
  setTimeout(() => { svg.style.transform = 'scale(1) translateY(0)'; }, 950);
}

/* Spread (or fold) Orion's wings — used before flight. */
export function orionSpreadWings(on) {
  const slot = activeOrionSlot;
  if (!slot) return;
  slot.querySelectorAll('.owl-wing-anim').forEach((w, i) => {
    w.style.transition = 'transform 0.45s cubic-bezier(0.34,1.56,0.64,1)';
    w.style.transformBox = 'fill-box';
    w.style.transformOrigin = i === 0 ? 'right center' : 'left center';
    w.style.transform = on ? `rotate(${i === 0 ? -32 : 32}deg) scaleX(1.25)` : '';
  });
}

/* Orion spreads his wings and flies toward a target element, then lands back
   in his corner. Returns a promise that resolves when he's home. */
export function orionFlyTo(targetEl, { hold = 650, returnHome = true, scale = 1.4 } = {}) {
  return new Promise((resolve) => {
    const slot = activeOrionSlot;
    if (!slot || !targetEl) { resolve(); return; }
    const s = slot.getBoundingClientRect();
    const t = targetEl.getBoundingClientRect();
    const dx = (t.left + t.width / 2) - (s.left + s.width / 2);
    const dy = (t.top + t.height / 2) - (s.top + s.height / 2);
    orionSpreadWings(true);
    slot.style.zIndex = '400';
    slot.style.transition = 'transform 0.85s cubic-bezier(0.4,0,0.2,1)';
    slot.style.transform = `translate(${dx}px, ${dy}px) scale(${scale})`;
    setTimeout(() => {
      if (returnHome) {
        slot.style.transform = 'translate(0,0) scale(1)';
        setTimeout(() => { orionSpreadWings(false); slot.style.zIndex = ''; resolve(); }, 850);
      } else {
        orionSpreadWings(false); resolve();
      }
    }, 850 + hold);
  });
}

/* Fly off-screen in a direction (used for the intake → board transition). */
export function orionFlyOut(dir = 'up') {
  return new Promise((resolve) => {
    const slot = activeOrionSlot;
    if (!slot) { resolve(); return; }
    orionSpreadWings(true);
    const map = { up: 'translate(-40vw,-80vh)', across: 'translate(80vw,-30vh)' };
    slot.style.zIndex = '400';
    slot.style.transition = 'transform 0.8s cubic-bezier(0.4,0,0.2,1)';
    slot.style.transform = `${map[dir] || map.up} scale(1.5)`;
    setTimeout(resolve, 720);
  });
}

/* Close one eye briefly, as if thinking. */
export function orionThink() {
  const lidL = document.getElementById('orionEyelidL');
  if (!lidL) return;
  lidL.setAttribute('y', '-92');
  setTimeout(() => lidL.setAttribute('y', '-107'), 650);
}

/* Tilt Orion's head toward a point (screen x). */
export function orionGlance(clientX) {
  const head = document.getElementById('orionHead');
  const slot = activeOrionSlot;
  if (!head || !slot) return;
  const rect = slot.getBoundingClientRect();
  const dir = clientX < rect.left + rect.width / 2 ? -12 : 12;
  head.style.transform = `rotate(${dir}deg)`;
  setTimeout(() => { head.style.transform = 'rotate(0deg)'; }, 1200);
}

const REMARKS = {
  duplicate: 'Interesting.',
  relationship: 'Follow this.',
  timeline: 'Something changed.',
  memory: 'I have seen this before.',
  hypothesis: 'Look closer.',
  conclusion: 'That explains it.',
  begin: "Every clue matters. Let's begin.",
};

/* React to a meaningful investigation moment with a gesture + subtitle. */
export function orionReact(kind) {
  const line = REMARKS[kind];
  if (kind === 'duplicate' || kind === 'relationship' || kind === 'conclusion') orionLeanIn();
  if (kind === 'hypothesis' || kind === 'memory') orionThink();
  if (line) orionSpeak(line);
}

export function setOrionState(state) {
  // state: 'idle', 'alert', 'investigating', 'satisfied', 'thinking'
  const head = document.getElementById('orionHead');
  if (state === 'thinking') orionThink();
  if (state === 'investigating' && head) {
    head.style.transform = 'rotate(0deg) translateY(4px)'; // looking down at evidence
  }
  if (state === 'idle' && head) head.style.transform = 'rotate(0deg)';
}

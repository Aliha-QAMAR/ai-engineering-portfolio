(function () {
  function rand(min, max) { return Math.random() * (max - min) + min; }

  const scene = document.querySelector('#screen-landing .ld-scene');
  if (!scene) return; // landing screen markup not present, bail safely

  /* ── Particles (dust / firefly / sparkle) ── */
  const PARTICLES = Array.from({ length: 38 }, (_, i) => ({
    id: i,
    x: rand(2, 98),
    y: rand(10, 88),
    size: rand(1.5, 3.5),
    dur: rand(7, 18),
    delay: rand(0, 12),
    kind: i < 22 ? 'dust' : i < 32 ? 'firefly' : 'sparkle',
  }));

  const particlesLayer = document.getElementById('ldParticles');
  PARTICLES.forEach(p => {
    let el;
    if (p.kind === 'firefly') {
      el = document.createElement('div');
      el.className = 'ld-firefly';
      el.style.left = p.x + '%';
      el.style.top = p.y + '%';
      el.style.width = (p.size + 2) + 'px';
      el.style.height = (p.size + 2) + 'px';
      el.style.boxShadow = `0 0 ${p.size * 5}px ${p.size * 2}px rgba(245,195,50,0.75)`;
      el.style.animation = `ld-firefly ${p.dur}s ease-in-out ${p.delay}s infinite`;
    } else if (p.kind === 'sparkle') {
      el = document.createElement('div');
      el.className = 'ld-sparkle-item';
      el.style.left = p.x + '%';
      el.style.top = p.y + '%';
      el.style.width = (p.size + 3) + 'px';
      el.style.animation = `ld-sparkle ${p.dur * 0.55}s ease-in-out ${p.delay}s infinite`;
      el.innerHTML = `<svg viewBox="0 0 10 10" style="width:100%"><path d="M5,0 L5.4,4.6 L10,5 L5.4,5.4 L5,10 L4.6,5.4 L0,5 L4.6,4.6 Z" fill="#e8c84a"/></svg>`;
    } else {
      el = document.createElement('div');
      el.className = 'ld-dust';
      el.style.left = p.x + '%';
      el.style.top = p.y + '%';
      el.style.width = p.size + 'px';
      el.style.height = p.size + 'px';
      el.style.animation = `ld-dust-float ${p.dur}s ease-in-out ${p.delay}s infinite`;
    }
    if (particlesLayer) particlesLayer.appendChild(el);
  });

  /* ── Falling leaves ── */
  const LEAVES = Array.from({ length: 10 }, (_, i) => ({
    id: i,
    x: rand(3, 92),
    size: rand(14, 26),
    dur: rand(14, 24),
    delay: rand(0, 18),
    rot: rand(0, 360),
  }));

  const leavesLayer = document.getElementById('ldLeaves');
  LEAVES.forEach(l => {
    const el = document.createElement('div');
    el.className = 'ld-leaf-item';
    el.style.left = l.x + '%';
    el.style.width = l.size + 'px';
    el.style.height = l.size + 'px';
    el.style.animation = `ld-leaf-fall ${l.dur}s ease-in ${l.delay}s infinite`;
    const hue = 22 + (l.rot % 30);
    const light = 34 + (l.rot % 12);
    el.innerHTML = `<svg viewBox="0 0 30 30" style="width:100%;opacity:0.82">
      <ellipse cx="15" cy="15" rx="12" ry="7" fill="hsl(${hue},58%,${light}%)"/>
      <path d="M3,15 Q15,9 27,15" stroke="rgba(255,210,130,0.35)" stroke-width="0.8" fill="none"/>
      <line x1="15" y1="8" x2="15" y2="22" stroke="rgba(255,210,130,0.25)" stroke-width="0.6"/>
    </svg>`;
    if (leavesLayer) leavesLayer.appendChild(el);
  });

  /* ── Butterflies ── */
  const BUTTERFLIES = Array.from({ length: 3 }, (_, i) => ({
    id: i,
    x: rand(8, 78),
    y: rand(12, 48),
    delay: rand(0, 6),
    s: rand(0.55, 0.9),
  }));

  const butterfliesLayer = document.getElementById('ldButterflies');
  BUTTERFLIES.forEach(b => {
    const el = document.createElement('div');
    el.className = 'ld-butterfly-item';
    el.style.left = b.x + '%';
    el.style.top = b.y + '%';
    el.style.transform = `scale(${b.s})`;
    el.style.animation = `ld-butterfly ${2.8 + b.delay * 0.3}s ease-in-out ${b.delay}s infinite`;
    el.innerHTML = `<svg viewBox="0 0 52 42" style="width:52px;opacity:0.68">
      <ellipse cx="13" cy="19" rx="12" ry="8" fill="rgba(185,140,75,0.65)"/>
      <ellipse cx="39" cy="19" rx="12" ry="8" fill="rgba(185,140,75,0.65)"/>
      <ellipse cx="15" cy="28" rx="8" ry="5" fill="rgba(165,118,55,0.5)"/>
      <ellipse cx="37" cy="28" rx="8" ry="5" fill="rgba(165,118,55,0.5)"/>
      <line x1="26" y1="14" x2="26" y2="35" stroke="rgba(70,42,18,0.7)" stroke-width="1.5"/>
    </svg>`;
    if (butterfliesLayer) butterfliesLayer.appendChild(el);
  });

  /* ── Ink ripple (injected as absolutely-positioned rings over the inkpot) ── */
  const inkpot = scene.querySelector('.ld-inkpot');
  function showRipple() {
    if (!inkpot) return;
    const r1 = document.createElement('div');
    r1.className = 'ld-ink-ripple r1';
    const r2 = document.createElement('div');
    r2.className = 'ld-ink-ripple r2';
    inkpot.appendChild(r1);
    inkpot.appendChild(r2);
    setTimeout(() => { r1.remove(); r2.remove(); }, 950);
  }

  /* ── Feather phase control ── */
  const feather = scene.querySelector('.ld-feather');
  const baseTransform = {
    idle: 'translateX(0px) translateY(0px) rotate(30deg)',
    rising: 'translateX(0px) translateY(0px) rotate(30deg)',
    sweeping: 'translateX(10px) translateY(-28px) rotate(-14deg)',
    settling: 'translateX(230px) translateY(-24px) rotate(-10deg)',
    resting: 'translateX(0px) translateY(0px) rotate(30deg)',
  };
  const animMap = {
    idle: '',
    rising: 'ld-feather-rise 0.85s cubic-bezier(0.34,1.4,0.64,1) forwards',
    sweeping: 'ld-feather-sweep 2.8s cubic-bezier(0.4,0,0.2,1) forwards',
    settling: 'ld-feather-settle 1s cubic-bezier(0.34,1.2,0.64,1) forwards',
    resting: '',
  };
  function setFeatherPhase(phase) {
    if (!feather) return;
    feather.style.transform = baseTransform[phase];
    feather.style.animation = animMap[phase];
  }

  /* ── Text / tagline / button reveal ── */
  const titleEl = scene.querySelector('.ld-title');
  const taglineSpans = scene.querySelectorAll('.ld-tagline span');
  const btnWrap = scene.querySelector('.ld-btn-wrap');

  function setTextVisible(v) {
    if (!titleEl) return;
    titleEl.classList.toggle('visible', v);
  }
  function setTaglineVisible(v) {
    taglineSpans.forEach((span, i) => {
      if (v) {
        span.style.transition = `opacity 0.65s ease ${0.25 + i * 0.42}s, transform 0.65s ease ${0.25 + i * 0.42}s`;
        span.classList.add('visible');
      } else {
        span.style.transition = 'none';
        span.classList.remove('visible');
      }
    });
  }
  function setButtonVisible(v) {
    if (!btnWrap) return;
    btnWrap.classList.toggle('visible', v);
  }

  /* ── Timing / sequencing ── */
  const timers = [];
  function schedule(fn, ms) {
    const id = setTimeout(fn, ms);
    timers.push(id);
  }
  function clearAllTimers() {
    timers.forEach(clearTimeout);
    timers.length = 0;
  }

  function runWriteCycle(isFirst) {
    setFeatherPhase('rising');
    showRipple();

    schedule(() => {
      setFeatherPhase('sweeping');
      if (!isFirst) {
        setTextVisible(false);
        schedule(() => setTextVisible(true), 100);
      } else {
        setTextVisible(true);
      }
    }, 900);

    schedule(() => {
      setFeatherPhase('settling');
      showRipple();
    }, 900 + 2900);

    schedule(() => {
      setFeatherPhase('resting');
      if (isFirst) {
        schedule(() => setTaglineVisible(true), 300);
        schedule(() => setButtonVisible(true), 1400);
      }
    }, 900 + 2900 + 1050);

    schedule(() => {
      runWriteCycle(false);
    }, 900 + 2900 + 1050 + 2400);
  }

  setFeatherPhase('idle');
  schedule(() => runWriteCycle(true), 1200);

  /* NOTE: no click handler is attached to #scrollCue here on purpose —
     that button's navigation (landing -> auth) is already wired up
     elsewhere (auth.js / main.js), as noted in the HTML comment. */
})();
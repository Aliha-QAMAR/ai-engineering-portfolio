/* ═══════════════════════════════════════════════════════════════════
   NOCTRA — Main Application Controller
   Beyond the Obvious.
═══════════════════════════════════════════════════════════════════ */

import { createDeskScene } from './scene.js';
import { createOrion, initOrionBehavior, orionSpeak } from './orion.js';
import { createRain, createDust, initLightning, createLightningOverlay } from './atmosphere.js';
import './sound.js';

const GOLD = '#c9a84c';
const CRIMSON = '#7a1a1a';

let currentScreen = null;

/* ─── Confidential Folder SVG ─────────────────────────────────────── */
function createFolder(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `
    <div class="folder-container" id="the-folder" style="position:relative;width:260px;cursor:pointer;filter:drop-shadow(0 12px 30px rgba(0,0,0,0.7));transition:transform 0.3s cubic-bezier(0.34,1.56,0.64,1), filter 0.3s ease;">
      <svg viewBox="0 0 260 340" width="260" height="340" style="overflow:visible;">
        <defs>
          <linearGradient id="fGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#c8a870"/>
            <stop offset="40%" stop-color="#b89458"/>
            <stop offset="100%" stop-color="#9a7840"/>
          </linearGradient>
          <linearGradient id="fTop" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#c8a870"/><stop offset="100%" stop-color="#b08840"/>
          </linearGradient>
        </defs>
        <ellipse cx="130" cy="340" rx="120" ry="16" fill="rgba(0,0,0,0.5)"/>
        <!-- Back panel -->
        <path d="M 10 40 Q 10 30 20 30 L 95 30 Q 105 30 110 20 L 150 20 Q 155 30 165 30 L 240 30 Q 250 30 250 40 L 250 320 Q 250 330 240 330 L 20 330 Q 10 330 10 320 Z" fill="#a07838"/>
        <!-- Front flap -->
        <g id="folder-flap" style="transform-origin:130px 330px;">
          <path d="M 10 55 Q 10 45 20 45 L 240 45 Q 250 45 250 55 L 250 320 Q 250 330 240 330 L 20 330 Q 10 330 10 320 Z" fill="url(#fGrad)"/>
          ${[0,1,2,3,4,5].map(i => `<line x1="10" y1="${75+i*42}" x2="250" y2="${75+i*42}" stroke="rgba(0,0,0,0.07)" stroke-width="1"/>`).join('')}
          <path d="M 85 45 L 85 30 Q 85 22 93 22 L 167 22 Q 175 22 175 30 L 175 45 Z" fill="url(#fTop)"/>
          <!-- Clasp -->
          <circle cx="130" cy="175" r="12" fill="#3a2510"/>
          <circle cx="130" cy="175" r="8" fill="#8a6830"/>
          <circle cx="130" cy="175" r="5" fill="#6a4820"/>
          <circle cx="128" cy="173" r="2" fill="rgba(255,255,255,0.2)"/>
          <!-- CONFIDENTIAL -->
          <text x="130" y="110" text-anchor="middle" font-family="'Cinzel', serif" font-size="12" font-weight="700" letter-spacing="3.5" fill="${CRIMSON}" opacity="0.9">CONFIDENTIAL</text>
          <rect x="28" y="96" width="204" height="21" rx="2" fill="none" stroke="${CRIMSON}" stroke-width="1.5" opacity="0.55"/>
          <text x="130" y="146" text-anchor="middle" font-family="'Courier Prime', monospace" font-size="8" fill="rgba(80,50,20,0.55)" letter-spacing="1">CASE FILE: NOC-2026-0001</text>
          <text x="130" y="240" text-anchor="middle" font-family="'Cinzel', serif" font-size="9" letter-spacing="5" fill="rgba(80,50,20,0.55)">NOCTRA</text>
          <rect x="20" y="40" width="220" height="8" rx="1" fill="#f0e8d5" opacity="0.55"/>
          <rect x="25" y="38" width="210" height="6" rx="1" fill="#ede3cc" opacity="0.38"/>
          <path d="M 220 310 L 250 310 L 250 330 Z" fill="rgba(0,0,0,0.12)"/>
          <!-- Open prompt -->
          <text id="folder-prompt" x="130" y="290" text-anchor="middle" font-family="'Cormorant Garamond', serif" font-size="10" letter-spacing="2" fill="rgba(80,50,20,0.35)" font-style="italic">Open Investigation</text>
        </g>
        <!-- Wax seal -->
        <g id="wax-seal" style="transform-origin:130px 175px;">
          <circle cx="130" cy="210" r="18" fill="#7a1818"/>
          <circle cx="130" cy="210" r="15" fill="#8b1a1a"/>
          <text x="130" y="215" text-anchor="middle" font-family="'Cinzel', serif" font-size="12" font-weight="600" fill="rgba(240,220,180,0.75)">N</text>
        </g>
      </svg>
    </div>
  `;

  const folderEl = document.getElementById('the-folder');
  const flapEl = document.getElementById('folder-flap');
  const sealEl = document.getElementById('wax-seal');
  const promptEl = document.getElementById('folder-prompt');

  // Hover effects
  folderEl.addEventListener('mouseenter', () => {
    if (folderEl.dataset.phase === 'opening') return;
    folderEl.style.transform = 'translateY(-8px) scale(1.012)';
    folderEl.style.filter = 'drop-shadow(0 20px 40px rgba(0,0,0,0.7))';
    if (promptEl) promptEl.setAttribute('fill', 'rgba(80,50,20,0.7)');
  });
  folderEl.addEventListener('mouseleave', () => {
    if (folderEl.dataset.phase === 'opening') return;
    folderEl.style.transform = 'none';
    folderEl.style.filter = 'drop-shadow(0 12px 30px rgba(0,0,0,0.7))';
    if (promptEl) promptEl.setAttribute('fill', 'rgba(80,50,20,0.35)');
  });

  // Click → open sequence
  folderEl.addEventListener('click', () => {
    if (folderEl.dataset.phase === 'opening') return;
    folderEl.dataset.phase = 'opening';
    folderEl.style.cursor = 'default';

    // 1. Crack wax seal
    sealEl.classList.add('seal-cracking');
    folderEl.style.transform = 'translateY(-12px) scale(1.02)';
    folderEl.style.filter = 'drop-shadow(0 30px 60px rgba(0,0,0,0.9)) drop-shadow(0 0 40px rgba(200,140,40,0.3))';

    // 2. Open folder flap
    setTimeout(() => {
      flapEl.classList.add('folder-opening');
      if (promptEl) promptEl.style.display = 'none';
    }, 500);

    // 3. Scene zoom → navigate to auth
    setTimeout(() => {
      const landingScreen = document.getElementById('landing-screen');
      if (landingScreen) {
        landingScreen.classList.add('scene-zooming');
        landingScreen.style.transformOrigin = '50% 60%';
      }
    }, 1300);

    // 4. Navigate to auth page
    setTimeout(() => {
      window.location.href = '/auth';
    }, 2200);
  });
}

/* ─── Landing Screen Init ──────────────────────────────────────── */
function initLanding() {
  currentScreen = 'landing';

  // Inject desk scene SVG
  createDeskScene('desk-scene');

  // Inject atmosphere
  createRain('window-rain');
  createRain('ambient-rain');
  createDust('dust-layer');
  initLightning(() => createLightningOverlay());

  // Inject Orion
  createOrion('orion-landing');
  initOrionBehavior();

  // Inject folder
  createFolder('folder-container');
}

/* ─── Auth Screen Init ─────────────────────────────────────────── */
function initAuth() {
  currentScreen = 'auth';

  // Initialize Orion on auth screen
  createOrion('orion-auth');
  initOrionBehavior();

  const btnLogin = document.getElementById('btn-login');
  const btnRegister = document.getElementById('btn-register');
  const errorDiv = document.getElementById('auth-error');
  const codenameInput = document.getElementById('auth-codename');
  const passwordInput = document.getElementById('auth-password');

  function showError(msg) {
    if (errorDiv) {
      errorDiv.textContent = msg;
      errorDiv.style.display = 'block';
    }
  }

  async function doAuth(endpoint) {
    const codename = codenameInput?.value?.trim();
    const password = passwordInput?.value?.trim();
    if (!codename || !password) {
      showError('Codename and passphrase are required for clearance.');
      return;
    }
    try {
      const res = await fetch(`/api/auth/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codename, password })
      });
      const data = await res.json();
      if (data.success) {
        // Show ACCESS GRANTED stamp
        const stamp = document.getElementById('access-granted-stamp');
        if (stamp) {
          stamp.style.display = 'block';
          stamp.classList.add('stamp-active');
        }
        orionSpeak('Clearance verified. Welcome aboard, investigator.');

        // Navigate to hub after stamp animation
        setTimeout(() => {
          window.location.href = '/hub';
        }, 1800);
      } else {
        showError(data.error || 'Access denied. Verify your credentials.');
      }
    } catch (err) {
      showError('Communication disrupted. Try again.');
    }
  }

  btnLogin?.addEventListener('click', () => doAuth('login'));
  btnRegister?.addEventListener('click', () => doAuth('register'));

  // Enter key submits login
  passwordInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') doAuth('login');
  });
}

/* ─── Hub Screen Init ──────────────────────────────────────────── */
function initHub() {
  currentScreen = 'hub';

  // Inject a simplified desk scene for background
  createDeskScene('hub-scene');

  // Atmosphere
  initLightning(() => createLightningOverlay());

  // Orion
  createOrion('orion-hub');
  initOrionBehavior();

  // Load user info
  fetch('/api/auth/status')
    .then(r => r.json())
    .then(data => {
      const nameEl = document.getElementById('hub-user-codename');
      if (nameEl && data.codename) {
        nameEl.textContent = `Agent: ${data.codename}`;
      }
    });

  // Desk item interactions
  const items = document.querySelectorAll('.desk-item');
  items.forEach(item => {
    item.addEventListener('mouseenter', () => {
      item.style.transform = 'translateY(-6px)';
      item.style.filter = 'drop-shadow(0 12px 24px rgba(200,140,40,0.3))';
    });
    item.addEventListener('mouseleave', () => {
      item.style.transform = 'none';
      item.style.filter = 'none';
    });
  });

  // New case button
  document.getElementById('item-new-case')?.addEventListener('click', () => {
    orionSpeak('A new case file awaits, investigator.');
    setTimeout(() => { window.location.href = '/investigation/new'; }, 500);
  });

  // Evidence wall — shows every case and the evidence already linked to
  // it, right on that page. Starting a NEW case still only happens from
  // "Begin Investigation".
  document.getElementById('item-evidence-wall')?.addEventListener('click', () => {
    orionSpeak('The evidence board reveals patterns the eye alone cannot see.');
    setTimeout(() => { window.location.href = '/evidence-board'; }, 500);
  });

  // Archive
  document.getElementById('item-archive')?.addEventListener('click', () => {
    orionSpeak('Past investigations hold the keys to present mysteries.');
    setTimeout(() => { window.location.href = '/archive'; }, 500);
  });

  // Memory vault
  document.getElementById('item-memory')?.addEventListener('click', () => {
    orionSpeak('Memories never truly fade — they wait to be rediscovered.');
    setTimeout(() => { window.location.href = '/memory'; }, 500);
  });

  // Search — the archive doubles as case search
  document.getElementById('item-search')?.addEventListener('click', () => {
    orionSpeak('Every detail, no matter how small, could break the case.');
    setTimeout(() => { window.location.href = '/archive'; }, 500);
  });

  // Settings
  document.getElementById('item-settings')?.addEventListener('click', () => {
    setTimeout(() => { window.location.href = '/settings'; }, 200);
  });

  // Logout
  document.getElementById('btn-logout')?.addEventListener('click', async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/';
  });

  // Hover effects on logout button
  const logoutBtn = document.getElementById('btn-logout');
  logoutBtn?.addEventListener('mouseenter', () => {
    logoutBtn.style.borderColor = 'rgba(201,168,76,0.6)';
    logoutBtn.style.color = 'rgba(201,168,76,0.9)';
  });
  logoutBtn?.addEventListener('mouseleave', () => {
    logoutBtn.style.borderColor = 'rgba(201,168,76,0.15)';
    logoutBtn.style.color = 'rgba(201,168,76,0.4)';
  });
}

/* ─── Access Screen Init ───────────────────────────────────────── */
function initAccess() {
  currentScreen = 'access';
  createOrion('orion-access');
  initOrionBehavior();

  // Auto-animate to auth after a delay
  const proceedBtn = document.getElementById('proceed-to-auth');
  proceedBtn?.addEventListener('click', () => {
    window.location.href = '/auth';
  });

  // Auto-reveal personnel file
  const personnelFile = document.getElementById('personnel-file');
  if (personnelFile) {
    setTimeout(() => {
      personnelFile.style.transition = 'transform 0.8s cubic-bezier(0.4,0,0.2,1), opacity 0.8s ease';
      personnelFile.style.transform = 'translate(-50%, -50%) scale(1)';
      personnelFile.style.opacity = '1';
    }, 600);
  }
}

/* ═══════════════════════════════════════════════════════════════════
   INITIALIZATION — Detect which screen we're on and initialize
═══════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('landing-screen')) {
    initLanding();
  } else if (document.getElementById('access-screen')) {
    initAccess();
  } else if (document.getElementById('auth-screen')) {
    initAuth();
  } else if (document.getElementById('hub-screen')) {
    initHub();
  }
});

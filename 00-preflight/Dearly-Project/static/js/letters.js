(function () {
  const MOOD_ICONS = { grateful: '🌤️', heavy: '🌧️', hopeful: '🌱', nostalgic: '🍂', lonely: '🌙', proud: '⭐' };
  let moodsCache = null;
  let mediaRecorder = null;
  let recordedChunks = [];

  async function apiRaw(path, opts) {
    opts = opts || {};
    const headers = opts.headers || {};
    const token = window.DearlyAuth.getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;
    if (opts.json) headers['Content-Type'] = 'application/json';
    return fetch('/api' + path, {
      method: opts.method || 'GET',
      headers,
      body: opts.json ? JSON.stringify(opts.json) : opts.body
    });
  }

  function bottleSvg() {
    return `<svg class="bottle-svg" viewBox="0 0 52 70"><g class="cork"><rect x="20" y="2" width="12" height="10" rx="2" fill="#b6924f"/></g>
      <path d="M20 12 h12 v10 c8 4 10 12 10 20 v20 c0 4 -3 6 -7 6 H17 c-4 0 -7 -2 -7 -6 V42 c0 -8 2 -16 10 -20 Z" fill="#3c5a3a" opacity=".85"/>
      <rect x="16" y="38" width="20" height="26" rx="2" fill="#eddcb2" opacity=".9" transform="rotate(-4 26 50)"/>
      </svg>`;
  }
  function flowerSvg() {
    return `<svg class="tile-flower" viewBox="0 0 40 40"><g fill="#8a3a45"><circle cx="20" cy="10" r="7"/><circle cx="30" cy="18" r="7"/><circle cx="26" cy="30" r="7"/><circle cx="12" cy="28" r="7"/><circle cx="8" cy="14" r="7"/></g><circle cx="20" cy="20" r="6" fill="#b6924f"/></svg>`;
  }

  // ============================================================
  // SHARED: seal + send flight animation, and envelope-open animation
  // ============================================================
  function playSendAnimation(panelBody, onDone) {
    panelBody.innerHTML = `
      <div class="send-stage">
        <div class="send-paper foldSend"></div>
        <svg class="send-envelope" viewBox="0 0 160 110">
          <rect x="6" y="14" width="148" height="88" rx="3" fill="#eddcb2" stroke="#a9895a" stroke-width="2"/>
          <path d="M6 14 L80 60 L154 14" fill="#e0c99a" stroke="#a9895a" stroke-width="2"/>
          <circle class="send-seal" cx="80" cy="58" r="14" fill="#6e2b36"/>
        </svg>
      </div>
      <p class="sub" style="text-align:center; margin-top:1.5rem;">Sealing and sending your letter…</p>
    `;
    const envelope = panelBody.querySelector('.send-envelope');
    const seal = panelBody.querySelector('.send-seal');
    setTimeout(() => envelope.classList.add('show'), 400);
    setTimeout(() => seal.classList.add('stamp'), 800);
    setTimeout(() => envelope.classList.add('flyAway'), 1300);
    setTimeout(onDone, 2150);
  }

  function showSentConfirm(panelBody) {
    panelBody.innerHTML = `<div class="sent-confirm"><div class="stamp-big"></div><p class="line" style="font-style:italic;">Your letter is sealed and sent.</p></div>
      <div class="panel-actions" style="justify-content:center; gap:.8rem;"><button class="btn btn-secondary" data-do="back-to-landing">← Back to Letters</button><button class="btn btn-primary" data-do="compose-another">✉️ Write Another</button></div>`;
    panelBody.querySelector('[data-do="back-to-landing"]').addEventListener('click', () => mountLettersLanding(panelBody));
    panelBody.querySelector('[data-do="compose-another"]').addEventListener('click', () => mountCompose(panelBody));
  }

  // anonymous bottle-mail pops its cork; every other letter opens as an
  // envelope whose flap lifts — then the burnt page rises out (below).
  function playOpenAnimation(iconEl, kind) {
    if (kind === 'anonymous') {
      iconEl.innerHTML = `
        <svg viewBox="0 0 52 70" style="width:120px; height:150px; overflow:visible;">
          <g class="cork corkPop"><rect x="20" y="2" width="12" height="10" rx="2" fill="#b6924f"/></g>
          <path d="M20 12 h12 v10 c8 4 10 12 10 20 v20 c0 4 -3 6 -7 6 H17 c-4 0 -7 -2 -7 -6 V42 c0 -8 2 -16 10 -20 Z" fill="#3c5a3a" opacity=".85"/>
          <rect x="16" y="38" width="20" height="26" rx="2" fill="#eddcb2" opacity=".95" transform="rotate(-4 26 50)"/>
        </svg>`;
      return;
    }
    const isPenpal = kind === 'penpal';
    iconEl.innerHTML = `
      <svg class="open-envelope" viewBox="0 0 130 100" style="width:150px;height:140px; overflow:visible;">
        <rect x="5" y="26" width="120" height="68" rx="3" fill="#eddcb2" stroke="#a9895a" stroke-width="2"/>
        ${isPenpal ? '' : '<circle cx="65" cy="60" r="16" fill="none" stroke="#6e2b36" stroke-width="2" opacity=".5"/>'}
        <path class="flap flapOpen" d="M5 26 L65 66 L125 26 Z" fill="#e0c99a" stroke="#a9895a" stroke-width="2"/>
      </svg>`;
  }

  function timeAgo(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  // ============================================================
  // INBOX
  // ============================================================
  async function mountInbox(panelBody, opts) {
    opts = opts || {};
    panelBody.innerHTML = `
      <h3>My Letters</h3>
      <p class="sub">Letters that found their way to you — tap one to open it</p>
      <div id="lettersList"><p style="color:var(--ink-soft); font-style:italic;">Fetching your letters…</p></div>
    `;
    wireInboxActions(panelBody);
    await loadInbox(panelBody);
  }

  async function loadInbox(panelBody) {
    const listEl = panelBody.querySelector('#lettersList');
    try {
      const res = await apiRaw('/letters/inbox');
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Could not load letters.');
      const letters = data.letters || [];
      if (!letters.length) {
        listEl.innerHTML = `<div class="empty-state"><div class="glyph">✉️</div><p class="line">The letter tray is empty.</p><small>Every envelope here will be one you actually wrote or received.</small></div>`;
        return;
      }
      listEl.innerHTML = `<div class="letter-tiles">${letters.map(tileHtml).join('')}</div>`;
      listEl.querySelectorAll('.letter-tile').forEach(tile => {
        tile.addEventListener('click', () => openLetter(panelBody, tile.dataset.id, letters.find(l => l.id === tile.dataset.id)));
      });
    } catch (err) {
      listEl.innerHTML = `<div class="error-note show">${err.message}</div>`;
    }
  }

  // a plain vintage envelope (used for "other" letters, and as the base
  // an added flower turns into a pen-pal envelope)
  function envelopeSvg() {
    return `<svg class="tile-env" viewBox="0 0 120 84"><rect x="6" y="14" width="108" height="60" rx="3" fill="#eddcb2" stroke="#a9895a" stroke-width="2"/><path d="M6 14 L60 52 L114 14" fill="#e0c99a" stroke="#a9895a" stroke-width="2"/><circle cx="60" cy="50" r="8" fill="#6e2b36"/></svg>`;
  }

  function tileHtml(l) {
    const kind = l.kind;
    // anonymous bottle-mail → sealed glass bottle
    if (kind === 'anonymous') {
      return `
        <div class="letter-tile ${l.opened ? '' : 'unopened'} tile-anonymous" data-id="${l.id}">
          <div class="tile-icon">${bottleSvg()}</div>
          <div class="tile-title">A letter, adrift</div>
          <div class="tile-meta">${timeAgo(l.created_at)}${l.mood ? ' · ' + (MOOD_ICONS[l.mood] || '') + ' ' + l.mood : ''}</div>
        </div>`;
    }
    // pen-pal → flowered envelope · anything else → plain envelope
    const flowered = kind === 'penpal';
    return `
      <div class="letter-tile ${l.opened ? '' : 'unopened'} tile-${kind}" data-id="${l.id}">
        ${flowered ? flowerSvg() : ''}
        <div class="tile-icon">${envelopeSvg()}</div>
        <div class="tile-title">${flowered ? ('From ' + (l.from || 'a pen pal')) : 'A letter'}</div>
        <div class="tile-meta">${timeAgo(l.created_at)}${l.mood ? ' · ' + (MOOD_ICONS[l.mood] || '') + ' ' + l.mood : ''}</div>
      </div>`;
  }

  async function openLetter(panelBody, id, meta) {
    const kind = meta.kind;
    const isPenpal = kind === 'penpal';
    const title = isPenpal ? ('From ' + meta.from)
      : (kind === 'anonymous' ? 'A letter adrift' : 'A letter');
    const sub = isPenpal ? 'A letter sealed with a flower'
      : (kind === 'anonymous' ? 'A bottle that drifted to you — pull the cork' : 'A letter that found its way to you');
    panelBody.innerHTML = `
      <h3>${title}</h3>
      <p class="sub">${sub}</p>
      <div class="open-stage">
        <div class="opening-icon" id="openingIcon"></div>
      </div>
      <div id="letterBody"></div>
      <div class="panel-actions" style="justify-content:flex-start; margin-top:1.2rem;">
        <button class="btn btn-secondary" data-do="back-to-inbox">← Back to my letters</button>
      </div>
    `;
    panelBody.querySelector('[data-do="back-to-inbox"]').addEventListener('click', () => mountInbox(panelBody));

    const iconEl = panelBody.querySelector('#openingIcon');
    playOpenAnimation(iconEl, kind);

    let letter;
    try {
      const res = await apiRaw(`/letters/${id}/open`, { method: 'POST', json: {} });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Could not open that letter.');
      letter = data.letter;
    } catch (err) {
      panelBody.querySelector('#letterBody').innerHTML = `<div class="error-note show">${err.message}</div>`;
      return;
    }

    setTimeout(() => {
      panelBody.querySelector('#letterBody').innerHTML = `
        <div class="burnt-paper paperRise">
          ${isPenpal ? `<span class="from-line">From ${meta.from}</span>` : ''}
          <div>${escapeHtml(letter.body).replace(/\n/g, '<br>')}</div>
        </div>
        <div class="letter-controls">
          <button class="speak-btn" data-do="speak">🔊 Speak aloud</button>
          <div class="speed-row"><span>Speed</span><input type="range" id="speedSlider" min="0.5" max="2" step="0.1" value="1"><span id="speedVal">1.0x</span></div>
          <button class="btn btn-secondary" data-do="reply">Reply</button>
        </div>
        <div id="replyArea"></div>
      `;
      wireLetterDetailActions(panelBody, letter, meta);
    }, 620);
  }

  function wireLetterDetailActions(panelBody, letter, meta) {
    const speedSlider = panelBody.querySelector('#speedSlider');
    const speedVal = panelBody.querySelector('#speedVal');
    speedSlider.addEventListener('input', () => { speedVal.textContent = parseFloat(speedSlider.value).toFixed(1) + 'x'; });

    panelBody.querySelector('[data-do="speak"]').addEventListener('click', async (e) => {
      const btn = e.currentTarget;
      const original = btn.textContent;
      btn.textContent = '🔊 Reading…';
      btn.disabled = true;
      try {
        const res = await apiRaw('/ai/tts', { method: 'POST', json: { text: letter.body, speed: parseFloat(speedSlider.value) } });
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.error || 'Could not read this aloud.');
        }
        const blob = await res.blob();
        const audio = new Audio(URL.createObjectURL(blob));
        audio.play();
        audio.onended = () => { btn.textContent = original; btn.disabled = false; };
      } catch (err) {
        alert(err.message);
        btn.textContent = original;
        btn.disabled = false;
      }
    });

    panelBody.querySelector('[data-do="reply"]').addEventListener('click', () => {
      const area = panelBody.querySelector('#replyArea');
      area.innerHTML = `
        <div class="reply-box">
          <textarea id="replyText" class="composer-field" placeholder="Write your reply..."></textarea>
          <div class="panel-actions">
            <button class="btn btn-primary" data-do="send-reply">Fold and send</button>
          </div>
        </div>`;
      area.querySelector('[data-do="send-reply"]').addEventListener('click', async () => {
        const text = area.querySelector('#replyText').value.trim();
        if (!text) return;
        try {
          const res = await apiRaw(`/letters/${letter.id}/reply`, { method: 'POST', json: { body: text } });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || 'Could not send that reply.');
          playSendAnimation(panelBody, () => showSentConfirm(panelBody));
        } catch (err) {
          alert(err.message);
        }
      });
    });
  }

  // ============================================================
  // COMPOSE
  // ============================================================
  async function mountCompose(panelBody) {
    if (!moodsCache) {
      try {
        const res = await apiRaw('/ai/mood-lines');
        const data = await res.json();
        moodsCache = res.ok ? data.moods : {};
      } catch (e) { moodsCache = {}; }
    }

    panelBody.innerHTML = `
      <h3>A new letter</h3>
      <p class="sub">Address it to a pen pal, or leave it be — it'll drift to someone in the room</p>
      <div class="compose-wrap">
        <div class="field-row">
          <label>To (optional — a pen pal's name)</label>
          <input type="text" id="composeTo" placeholder="Leave blank to send it into the room, anonymously">
        </div>
        <div class="field-row">
          <label>What's the mood?</label>
          <div class="mood-chips" id="moodChips">
            ${Object.keys(moodsCache).map(m => `<span class="mood-chip" data-mood="${m}">${MOOD_ICONS[m] || ''} ${m}</span>`).join('')}
          </div>
        </div>
        <div class="compose-parchment">
          <div class="compose-quill" aria-hidden="true">
            <svg viewBox="0 0 100 132" style="width:100%; display:block;">
              <ellipse cx="42" cy="120" rx="30" ry="6" fill="rgba(0,0,0,.28)"/>
              <path d="M18 92 Q14 98 14 108 Q14 122 42 124 Q70 122 70 108 Q70 98 66 92 Z" fill="#33231a"/>
              <ellipse cx="42" cy="92" rx="24" ry="6" fill="#241812"/>
              <ellipse cx="42" cy="92" rx="17" ry="4" fill="#0c0806"/>
              <g transform="rotate(22 42 92)">
                <path d="M42 92 L53 16" stroke="#5c3d1e" stroke-width="2.4" stroke-linecap="round" fill="none"/>
                <path d="M53 16 C71 20 75 40 61 64 C59 40 51 28 53 16 Z" fill="#efe6d2" stroke="rgba(150,120,70,.4)" stroke-width=".5"/>
                <path d="M53 16 C35 20 31 40 45 64 C47 40 55 28 53 16 Z" fill="#e4dabf" stroke="rgba(150,120,70,.4)" stroke-width=".5"/>
                <line x1="53" y1="22" x2="57" y2="60" stroke="rgba(150,120,70,.5)" stroke-width=".8"/>
              </g>
            </svg>
          </div>
          <div class="compose-textarea-wrap">
            <textarea class="composer-field burnt-field" id="composeText" placeholder="Begin your letter..."></textarea>
            <button class="mic-btn" id="micBtn" title="Speak instead of typing">🎙️</button>
          </div>
        </div>
        <div class="ai-help-row">
          <button class="btn btn-secondary" data-do="ai-help" type="button">🪶 Ask AI for a little help</button>
        </div>
        <div id="aiSuggestion"></div>
        <div class="panel-actions">
          <button class="btn btn-primary" data-do="send-compose">Seal and send</button>
        </div>
        <div class="error-note" id="composeError"></div>
      </div>
    `;
    wireCompose(panelBody);
  }

  function wireCompose(panelBody) {
    const textarea = panelBody.querySelector('#composeText');
    const errEl = panelBody.querySelector('#composeError');

    panelBody.querySelectorAll('.mood-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        panelBody.querySelectorAll('.mood-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        const mood = chip.dataset.mood;
        if (!textarea.value.trim() && moodsCache[mood]) textarea.value = moodsCache[mood];
      });
    });

    panelBody.querySelector('#micBtn').addEventListener('click', (e) => {
      toggleRecording(e.currentTarget, (text) => {
        textarea.value = textarea.value.trim() ? (textarea.value.trim() + ' ' + text) : text;
      });
    });

    panelBody.querySelector('[data-do="ai-help"]').addEventListener('click', async (e) => {
      const btn = e.currentTarget;
      const original = btn.textContent;
      btn.textContent = '🪶 Thinking…';
      btn.disabled = true;
      try {
        const res = await apiRaw('/ai/help', { method: 'POST', json: { draft: textarea.value, kind: 'letter' } });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Could not reach writing help.');
        panelBody.querySelector('#aiSuggestion').innerHTML = `
          <div class="ai-suggestion">
            <span>${escapeHtml(data.suggestion)}</span>
            <button class="btn btn-secondary" data-do="insert-suggestion" style="white-space:nowrap;">Use this</button>
          </div>`;
        panelBody.querySelector('[data-do="insert-suggestion"]').addEventListener('click', () => {
          textarea.value = textarea.value.trim() ? (textarea.value.trim() + '\n' + data.suggestion) : data.suggestion;
        });
      } catch (err) {
        panelBody.querySelector('#aiSuggestion').innerHTML = `<div class="error-note show">${err.message}</div>`;
      } finally {
        btn.textContent = original;
        btn.disabled = false;
      }
    });

    panelBody.querySelector('[data-do="send-compose"]').addEventListener('click', async (e) => {
      const to = panelBody.querySelector('#composeTo').value.trim();
      const activeMood = panelBody.querySelector('.mood-chip.active');
      const body = textarea.value.trim();
      errEl.classList.remove('show');
      if (!body) { errEl.textContent = 'A letter needs some words in it.'; errEl.classList.add('show'); return; }
      const btn = e.currentTarget;
      btn.disabled = true;
      try {
        const res = await apiRaw('/letters/send', { method: 'POST', json: { to, body, mood: activeMood ? activeMood.dataset.mood : '' } });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Could not send that letter.');
        playSendAnimation(panelBody, () => showSentConfirm(panelBody));
      } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.add('show');
        btn.disabled = false;
      }
    });
  }

  // Shared voice capture: click once to start recording via the mic,
  // click again to stop — the audio goes to /ai/stt (Whisper) and the
  // resulting text is handed back through onText. Used by both the
  // letter composer and the journal writing desk.
  async function toggleRecording(micBtn, onText) {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recordedChunks = [];
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (e) => recordedChunks.push(e.data);
      mediaRecorder.onstop = async () => {
        micBtn.classList.remove('recording');
        micBtn.textContent = '⏳';
        const blob = new Blob(recordedChunks, { type: 'audio/webm' });
        const form = new FormData();
        form.append('audio', blob, 'recording.webm');
        try {
          const res = await apiRaw('/ai/stt', { method: 'POST', body: form });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || 'Could not transcribe that.');
          onText(data.text);
        } catch (err) {
          alert(err.message);
        } finally {
          micBtn.textContent = '🎙️';
        }
        stream.getTracks().forEach(t => t.stop());
      };
      mediaRecorder.start();
      micBtn.classList.add('recording');
      micBtn.textContent = '⏹️';
    } catch (err) {
      alert('Could not access the microphone: ' + err.message);
    }
  }

  window.DearlyVoice = { toggle: toggleRecording };

  function wireInboxActions(panelBody) {
    const composeBtn = panelBody.querySelector('[data-do="compose"]');
    if (composeBtn) composeBtn.addEventListener('click', () => mountCompose(panelBody));
    const inboxBtn = panelBody.querySelector('[data-do="open-inbox"]');
    if (inboxBtn) inboxBtn.addEventListener('click', () => mountInbox(panelBody));
  }

  async function mountLettersLanding(panelBody) {
    panelBody.innerHTML = `
      <h3>Letters</h3>
      <p class="sub">A place to share words across time and distance</p>
      <div class="panel-actions" style="justify-content:center; gap:1rem; margin:2rem 0; flex-direction:column; max-width:400px; margin-left:auto; margin-right:auto;">
        <button class="btn btn-primary" data-do="view-inbox" style="padding:.9rem 1.8rem; font-size:1.05rem;">📬 View My Letters</button>
        <button class="btn btn-secondary" data-do="compose" style="padding:.9rem 1.8rem; font-size:1.05rem;">✉️ Write a New Letter</button>
      </div>
      <div class="empty-state">
        <div class="glyph">✉️</div>
        <p class="line">Open envelopes you've received with beautiful animations.</p>
        <small>Or compose a fresh letter to send to a pen pal or into the room.</small>
      </div>
    `;
    const viewBtn = panelBody.querySelector('[data-do="view-inbox"]');
    const composeBtn = panelBody.querySelector('[data-do="compose"]');
    if (viewBtn) viewBtn.addEventListener('click', () => mountInbox(panelBody));
    if (composeBtn) composeBtn.addEventListener('click', () => mountCompose(panelBody));
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  window.DearlyLetters = {
    mount(panelBody, opts) {
      opts = opts || {};
      if (opts.view === 'compose') mountCompose(panelBody);
      else if (opts.view === 'inbox') mountInbox(panelBody);
      else mountLettersLanding(panelBody);
    }
  };
})();
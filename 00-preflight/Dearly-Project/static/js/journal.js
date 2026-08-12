(function () {
  async function apiRaw(path, opts) {
    opts = opts || {};
    const headers = opts.headers || {};
    const token = window.DearlyAuth.getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;
    if (opts.json) headers['Content-Type'] = 'application/json';
    return fetch('/api' + path, {
      method: opts.method || 'GET',
      headers,
      body: opts.json ? JSON.stringify(opts.json) : undefined
    });
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }
  function fmtDate(iso) {
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  async function mount(panelBody, opts) {
    opts = opts || {};
    const tab = opts.tab || 'landing';

    // WRITE MODE — a clean "new journal" page (opened from "Begin a new page")
    if (tab === 'write') {
      panelBody.innerHTML = `
        <h3>Write a journal</h3>
        <p class="sub">A page for you, or a page for the room</p>
        <div id="journalTabBody"></div>
      `;
      renderWrite(panelBody.querySelector('#journalTabBody'), panelBody);
      return;
    }

    // VIEW MODE — browse pages that already exist (no writing here;
    // new pages are started from "Begin a new page")
    panelBody.innerHTML = `
      <h3>Journal</h3>
      <p class="sub">Pages you've written, and pages shared with the room</p>
      <div class="journal-tabs">
        <button class="journal-tab" data-tab="mine">My entries</button>
        <button class="journal-tab" data-tab="book">The public book</button>
        <button class="journal-tab" data-tab="penpals">Pen pal pages</button>
      </div>
      <div id="journalTabBody"></div>
    `;
    panelBody.querySelectorAll('.journal-tab').forEach(btn => {
      btn.addEventListener('click', () => renderTab(panelBody, btn.dataset.tab));
    });
    renderTab(panelBody, tab === 'landing' ? 'mine' : tab);
  }

  function setActiveTab(panelBody, tab) {
    panelBody.querySelectorAll('.journal-tab').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  }

  async function renderTab(panelBody, tab) {
    setActiveTab(panelBody, tab);
    const body = panelBody.querySelector('#journalTabBody');
    if (tab === 'write') return renderWrite(body, panelBody);
    body.innerHTML = `<p style="color:var(--ink-soft); font-style:italic;">Turning the pages…</p>`;
    let endpoint = tab === 'mine' ? '/journals/mine' : tab === 'book' ? '/journals/public' : '/journals/penpals';
    try {
      const res = await apiRaw(endpoint);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Could not load journals.');
      renderList(body, data.journals || [], tab);
    } catch (err) {
      body.innerHTML = `<div class="error-note show">${err.message}</div>`;
    }
  }

  function renderList(body, journals, tab) {
    if (!journals.length) {
      const messages = {
        mine: 'You haven\'t written any pages yet — start one from “Begin a new page.”',
        book: 'No pages have been shared with the room yet.',
        penpals: 'None of your pen pals have shared a page yet.'
      };
      body.innerHTML = `<div class="empty-state"><div class="glyph">📔</div><p class="line">${messages[tab]}</p></div>`;
      return;
    }
    body.innerHTML = `<div class="book-list">${journals.map(j => entryHtml(j, tab)).join('')}</div>`;
    body.querySelectorAll('[data-read-aloud]').forEach(btn => {
      btn.addEventListener('click', () => readAloud(btn, journals.find(j => j.id === btn.dataset.readAloud)));
    });
  }

  function entryHtml(j, tab) {
    return `
      <div class="book-entry">
        <div class="be-head">
          <span class="be-title">${escapeHtml(j.title || 'Untitled entry')}</span>
          ${j.author ? `<span class="be-author">by ${escapeHtml(j.author)}</span>` : ''}
        </div>
        ${j.topic ? `<div class="be-topic">${escapeHtml(j.topic)}</div>` : ''}
        <div class="be-body">${escapeHtml(j.body)}</div>
        <div class="be-foot">
          <span class="be-when">${fmtDate(j.created_at)}</span>
          <button class="speak-btn" data-read-aloud="${j.id}">🔊 Read aloud</button>
        </div>
      </div>`;
  }

  async function readAloud(btn, journal) {
    if (!journal) return;
    const original = btn.textContent;
    btn.textContent = '🔊 Reading…';
    btn.disabled = true;
    try {
      const res = await apiRaw('/ai/tts', { method: 'POST', json: { text: journal.body } });
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
  }

  function renderWrite(body, panelBody) {
    body.innerHTML = `
      <div class="field-row">
        <label>Title</label>
        <input type="text" id="jTitle" placeholder="Give this page a name">
      </div>
      <div class="field-row">
        <label>Topic (optional)</label>
        <input type="text" id="jTopic" placeholder="gratitude, a hard day, a small joy...">
      </div>
      <div class="field-row">
        <label>Who can read this?</label>
        <div class="visibility-row">
          <span class="vis-chip active" data-vis="private">Just me</span>
          <span class="vis-chip" data-vis="penpals">My pen pals</span>
          <span class="vis-chip" data-vis="public">The public book</span>
        </div>
      </div>
      <div class="journal-area" id="jBody" contenteditable="true" spellcheck="false" data-placeholder="Dear diary..."></div>
      <div class="ai-help-row" style="margin-top:1rem;">
        <button class="btn btn-secondary" data-do="ai-help" type="button">🪶 Ask AI for a little help</button>
      </div>
      <div id="jAiSuggestion"></div>
      <div class="panel-actions">
        <button class="btn btn-primary" data-do="save">Save entry</button>
      </div>
      <div class="error-note" id="jError"></div>
    `;
    let visibility = 'private';
    body.querySelectorAll('.vis-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        body.querySelectorAll('.vis-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        visibility = chip.dataset.vis;
      });
    });

    const field = body.querySelector('#jBody');
    body.querySelector('[data-do="ai-help"]').addEventListener('click', async (e) => {
      const btn = e.currentTarget;
      const original = btn.textContent;
      btn.textContent = '🪶 Thinking…';
      btn.disabled = true;
      try {
        const res = await apiRaw('/ai/help', { method: 'POST', json: { draft: field.textContent, kind: 'journal' } });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Could not reach writing help.');
        body.querySelector('#jAiSuggestion').innerHTML = `
          <div class="ai-suggestion">
            <span>${escapeHtml(data.suggestion)}</span>
            <button class="btn btn-secondary" data-do="insert" style="white-space:nowrap;">Use this</button>
          </div>`;
        body.querySelector('[data-do="insert"]').addEventListener('click', () => {
          field.textContent = field.textContent.trim() ? (field.textContent.trim() + '\n' + data.suggestion) : data.suggestion;
        });
      } catch (err) {
        body.querySelector('#jAiSuggestion').innerHTML = `<div class="error-note show">${err.message}</div>`;
      } finally {
        btn.textContent = original;
        btn.disabled = false;
      }
    });

    body.querySelector('[data-do="save"]').addEventListener('click', async (e) => {
      const errEl = body.querySelector('#jError');
      errEl.classList.remove('show');
      const title = body.querySelector('#jTitle').value.trim();
      const topic = body.querySelector('#jTopic').value.trim();
      const text = field.textContent.trim();
      if (!text) { errEl.textContent = 'A blank page isn\'t a journal entry yet.'; errEl.classList.add('show'); return; }
      const btn = e.currentTarget;
      btn.disabled = true;
      try {
        const res = await apiRaw('/journals', { method: 'POST', json: { title, topic, body: text, visibility } });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Could not save that entry.');
        mount(panelBody, { tab: 'mine' });
      } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.add('show');
        btn.disabled = false;
      }
    });
  }

  window.DearlyJournal = { mount };
})();
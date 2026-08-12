(function () {
  // ---------- guard: dashboard should never be reachable while signed out ----------
  document.addEventListener('screenchange', (e) => {
    if (e.detail.screen === 'dashboard' && !window.DearlyAuth.isSignedIn()) {
      Router.back();
    }
  });

  // ---------- local, in-memory placeholders for the pieces that don't
  // have a dedicated module yet (recordings are still a future part) ----------
  const store = {
    recordings: [] // {label}
  };

  // ---------- Memory Collector (camera) helpers ----------
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
  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  let cameraFileInput = document.getElementById('cameraFileInput');
  if (!cameraFileInput) {
    cameraFileInput = document.createElement('input');
    cameraFileInput.type = 'file';
    cameraFileInput.accept = 'image/*';
    cameraFileInput.id = 'cameraFileInput';
    cameraFileInput.style.display = 'none';
    document.body.appendChild(cameraFileInput);
  }

  function memoryEmptyState() {
    return `
      <h3>Memory Collector</h3>
      <p class="sub">Pick a photograph and let the room read it back to you</p>
      <div class="empty-state"><div class="glyph">📷</div><p class="line">The album is empty.</p><small>Upload a photo and Dearly will help you turn it into a memory.</small></div>
      <div class="panel-actions">
        <button class="btn btn-primary" data-do="upload-photo">Upload a photo</button>
      </div>
    `;
  }

  async function handlePhotoChosen(file) {
    panelBody.innerHTML = `
      <h3>Memory Collector</h3>
      <div class="photo-loading">
        <div class="photo-loading-frame"></div>
        <p class="sub">A memory is developing…</p>
      </div>
    `;
    const form = new FormData();
    form.append('image', file, file.name || 'memory.jpg');
    try {
      const res = await apiRaw('/ai/analyze-image', { method: 'POST', body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Could not read that photo.');
      renderPhotoAnalysis(data.analysis, data.image);
    } catch (err) {
      panelBody.innerHTML = `
        <h3>Memory Collector</h3>
        <div class="error-note show">${escapeHtml(err.message)}</div>
        <div class="panel-actions"><button class="btn btn-secondary" data-do="upload-photo">Try another photo</button></div>
      `;
    }
  }

  function renderPhotoAnalysis(a, imageDataUrl) {
    panelBody.innerHTML = `
      <h3>A memory, developed</h3>
      <p class="sub">Here's what the room noticed</p>
      <div class="memory-photo-wrap">
        <img class="memory-photo" src="${imageDataUrl}" alt="Uploaded memory">
      </div>
      <div class="memory-sections">
        <div class="memory-section"><h4>What I See</h4><p>${escapeHtml(a.what_i_see)}</p></div>
        <div class="memory-section"><h4>Atmosphere</h4><p>${escapeHtml(a.atmosphere)}</p></div>
        <div class="memory-section"><h4>Dominant Colors</h4><p>${escapeHtml(a.dominant_colors)}</p></div>
        <div class="memory-section"><h4>Possible Setting</h4><p>${escapeHtml(a.possible_setting)}</p></div>
        <div class="memory-section"><h4>Detected Emotions</h4><p>${escapeHtml(a.detected_emotions)}</p></div>
        <div class="memory-section memory-story"><h4>Story It Reminds Me Of</h4><p>${escapeHtml(a.story)}</p></div>
      </div>
      <div class="memory-actions">
        <button class="btn btn-secondary" data-do="mem-journal">Turn into Journal</button>
        <button class="btn btn-secondary" data-do="mem-letter">Write a Letter</button>
        <button class="btn btn-secondary" data-do="mem-timeline">Add to Timeline</button>
        <button class="btn btn-secondary" data-do="mem-archive">Archive Memory</button>
      </div>
      <div class="memory-note" id="memoryNote"></div>
    `;
    panelBody.dataset.memStory = a.story;
    panelBody.dataset.memTitle = a.possible_setting ? ('A memory: ' + a.possible_setting) : 'A memory';
  }

  // ---------- Archives (bookshelf): journals + opened letters, by year ----------
  async function mountArchives() {
    panelBody.innerHTML = `
      <h3>Archives</h3>
      <p class="sub">Old journals and kept letters, dusted off by year</p>
      <div id="archivesBody"><p style="color:var(--ink-soft); font-style:italic;">Dusting off the shelf…</p></div>
    `;
    const body = panelBody.querySelector('#archivesBody');
    try {
      const [jRes, lRes] = await Promise.all([apiRaw('/journals/mine'), apiRaw('/letters/inbox')]);
      const jData = await jRes.json();
      const lData = await lRes.json();
      if (!jRes.ok) throw new Error(jData.error || 'Could not open the shelf.');
      if (!lRes.ok) throw new Error(lData.error || 'Could not open the shelf.');
      const journals = (jData.journals || []).map(j => Object.assign({}, j, { _type: 'journal' }));
      const letters = (lData.letters || []).filter(l => l.opened).map(l => Object.assign({}, l, { _type: 'letter' }));
      const items = journals.concat(letters);
      if (!items.length) {
        body.innerHTML = `<div class="empty-state"><div class="glyph">📚</div><p class="line">The shelf is still empty.</p><small>Journals you write and letters you open will settle here, sorted by year.</small></div>`;
        return;
      }
      const byYear = {};
      items.forEach(it => {
        const y = new Date(it.created_at).getFullYear();
        (byYear[y] = byYear[y] || []).push(it);
      });
      const years = Object.keys(byYear).sort((a, b) => b - a);
      const colors = ['#6e2b36', '#3c5a3a', '#7a5230', '#4a3b2c', '#8a3a45', '#6b7245'];
      body.innerHTML = `
        <div class="year-shelf">
          ${years.map((y, i) => `<div class="year-book" data-year="${y}" style="background:${colors[i % colors.length]}">${y}</div>`).join('')}
        </div>
        <div id="archiveYearBody" style="margin-top:1.4rem;"></div>
      `;
      body.querySelectorAll('.year-book').forEach(el => {
        el.addEventListener('click', () => {
          body.querySelectorAll('.year-book').forEach(b => b.classList.remove('open'));
          el.classList.add('open');
          renderArchiveYear(byYear[el.dataset.year], el.dataset.year);
        });
      });
      body.querySelector('.year-book').classList.add('open');
      renderArchiveYear(byYear[years[0]], years[0]);
    } catch (err) {
      body.innerHTML = `<div class="error-note show">${escapeHtml(err.message)}</div>`;
    }
  }

  function archiveEntryTitle(it) {
    if (it._type === 'journal') return it.title || 'Untitled entry';
    if (it.kind === 'penpal') return 'A letter from ' + it.from;
    return 'A letter, adrift';
  }

  function renderArchiveYear(items, year) {
    const wrap = panelBody.querySelector('#archiveYearBody');
    if (!wrap) return;
    wrap.classList.remove('pageFlipIn');
    void wrap.offsetWidth; // restart the animation each time a shelf is opened
    items = items.slice().sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    wrap.innerHTML = `
      <h4 class="archive-year-heading">${year}</h4>
      <div class="book-list">
        ${items.map(it => `
          <div class="book-entry">
            <div class="be-head">
              <span class="be-title">${escapeHtml(archiveEntryTitle(it))}</span>
              <span class="be-author">${it._type === 'journal' ? 'journal' : 'letter'}</span>
            </div>
            <div class="be-body">${escapeHtml((it.body || '').slice(0, 220))}${(it.body || '').length > 220 ? '…' : ''}</div>
            <div class="be-foot"><span class="be-when">${new Date(it.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span></div>
          </div>`).join('')}
      </div>
    `;
    wrap.classList.add('pageFlipIn');
  }

  async function saveMemoryAsJournal(topic, noteText) {
    const noteEl = panelBody.querySelector('#memoryNote');
    const story = panelBody.dataset.memStory || '';
    const title = panelBody.dataset.memTitle || 'A memory';
    try {
      const res = await apiRaw('/journals', { method: 'POST', json: { title, topic, body: story, visibility: 'private' } });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Could not save that memory.');
      if (noteEl) { noteEl.textContent = noteText; noteEl.classList.add('show'); }
    } catch (err) {
      if (noteEl) { noteEl.textContent = err.message; noteEl.classList.add('show', 'error'); }
    }
  }

  // ---------- falling leaves ----------
  const leafColors = ['#8a3a45', '#b6924f', '#6b7245', '#a9642f'];
  const leavesWrap = document.getElementById('leaves');
  for (let i = 0; i < 14; i++) {
    const l = document.createElement('div');
    l.className = 'leaf';
    const size = 10 + Math.random() * 10;
    l.style.left = (Math.random() * 100) + '%';
    l.style.animationDuration = (10 + Math.random() * 10) + 's';
    l.style.animationDelay = (-Math.random() * 20) + 's';
    l.innerHTML = `<svg width="${size}" height="${size}" viewBox="0 0 20 20"><path d="M10 0 C16 6 18 14 10 20 C2 14 4 6 10 0Z" fill="${leafColors[i % 4]}"/></svg>`;
    leavesWrap.appendChild(l);
  }
  const dustWrap = document.getElementById('dust');
  for (let i = 0; i < 24; i++) {
    const d = document.createElement('div');
    d.className = 'speck';
    d.style.left = (Math.random() * 100) + '%';
    d.style.top = (Math.random() * 100) + '%';
    d.style.animationDuration = (6 + Math.random() * 8) + 's';
    d.style.animationDelay = (-Math.random() * 8) + 's';
    dustWrap.appendChild(d);
  }

  // ---------- candle day/night toggle ----------
  const candle = document.getElementById('obj-candle');
  const candleLabel = document.getElementById('candleLabel');
  candle.addEventListener('click', () => {
    document.body.classList.toggle('night');
    candleLabel.textContent = document.body.classList.contains('night') ? 'Light the room' : 'Dim the room';
  });
  candle.addEventListener('keypress', e => { if (e.key === 'Enter') candle.click(); });

  // ---------- overlay panel content ----------
  const overlay = document.getElementById('overlay');
  const panelBody = document.getElementById('panelBody');
  let currentPanelKey = null;
  const today = new Date();
  const todayStr = today.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

  // simple stubs for the two pieces that don't have a full module yet
  const renderers = {
    pen() {
      return `
        <h3>Begin a new page</h3>
        <p class="sub">What would you like to write?</p>
        <div class="grid-cards">
          <div class="card" data-do="new-journal" style="cursor:pointer;"><div class="icon">📔</div><div class="name">Journal entry</div><div class="meta">for yourself</div></div>
          <div class="card" data-do="new-letter" style="cursor:pointer;"><div class="icon">✉️</div><div class="name">A letter</div><div class="meta">to someone</div></div>
          <div class="card" data-do="upload-photo" style="cursor:pointer;"><div class="icon">📷</div><div class="name">From a photo</div><div class="meta">let the picture speak</div></div>
        </div>
      `;
    },
    camera() {
      return memoryEmptyState();
    },
    calendar() {
      return `
        <h3>Timeline</h3>
        <div class="empty-state"><div class="glyph">🕰️</div><p class="line">A woven view of your journals and letters, by date.</p><small>Open your Journal or Letters to see everything you've written so far.</small></div>
      `;
    }
  };

  function openPanel(key) {
    currentPanelKey = key;
    overlay.classList.add('open');

    if (key === 'diary') {
      panelBody.innerHTML = '';
      window.DearlyJournal.mount(panelBody, { tab: 'landing' });
    } else if (key === 'bookshelf') {
      panelBody.innerHTML = '';
      mountArchives();
    } else if (key === 'letters') {
      panelBody.innerHTML = '';
      window.DearlyLetters.mount(panelBody, { view: 'inbox' });
    } else if (key === 'globe') {
      panelBody.innerHTML = '';
      window.DearlyPenpals.mount(panelBody, { tab: 'search' });
    } else if (key === 'ink') {
      panelBody.innerHTML = '';
      window.DearlyLetters.mount(panelBody, { view: 'compose' });
    } else {
      panelBody.innerHTML = renderers[key] ? renderers[key]() : '<h3>Coming soon</h3>';
    }
  }
  document.getElementById('closePanel').addEventListener('click', () => overlay.classList.remove('open'));
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.classList.remove('open'); });

  [['obj-diary', 'diary'], ['obj-letters', 'letters'], ['obj-pen', 'pen'],
   ['obj-bookshelf', 'bookshelf'], ['obj-globe', 'globe'], ['obj-calendar', 'calendar']]
    .forEach(([id, key]) => {
      const el = document.getElementById(id);
      el.addEventListener('click', () => openPanel(key));
      el.addEventListener('keypress', e => { if (e.key === 'Enter') openPanel(key); });
    });

  // ---------- ink bottle: a quick, private journal page (distinct from
  // "New page", which asks what kind of page to start first) ----------
  const inkObj = document.getElementById('obj-ink');
  inkObj.addEventListener('click', () => {
    overlay.classList.add('open');
    panelBody.innerHTML = '';
    window.DearlyJournal.mount(panelBody, { tab: 'write' });
  });
  inkObj.addEventListener('keypress', e => { if (e.key === 'Enter') inkObj.click(); });

  // ---------- camera: opens the file explorer directly, with a quick
  // shutter-flash on the object itself before the picker appears ----------
  const cameraObj = document.getElementById('obj-camera');
  cameraObj.addEventListener('click', () => {
    cameraObj.classList.add('snapping');
    setTimeout(() => cameraObj.classList.remove('snapping'), 500);
    cameraFileInput.value = '';
    cameraFileInput.click();
  });
  cameraObj.addEventListener('keypress', e => { if (e.key === 'Enter') cameraObj.click(); });
  cameraFileInput.addEventListener('change', () => {
    const file = cameraFileInput.files && cameraFileInput.files[0];
    if (!file) return;
    overlay.classList.add('open');
    handlePhotoChosen(file);
  });

  // ---------- delegated actions inside the simple (non-module) panels ----------
  panelBody.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-do]');
    if (!btn) return;
    const action = btn.dataset.do;

    if (action === 'upload-photo') {
      cameraFileInput.value = '';
      cameraFileInput.click();
    } else if (action === 'new-journal') {
      window.DearlyJournal.mount(panelBody, { tab: 'write' });
    } else if (action === 'new-letter') {
      window.DearlyLetters.mount(panelBody, { view: 'compose' });
    } else if (action === 'mem-journal') {
      const story = panelBody.dataset.memStory || '';
      window.DearlyJournal.mount(panelBody, { tab: 'write' });
      setTimeout(() => {
        const jBody = panelBody.querySelector('#jBody');
        const jTitle = panelBody.querySelector('#jTitle');
        if (jBody) jBody.textContent = story;
        if (jTitle) jTitle.value = panelBody.dataset.memTitle || 'A memory';
      }, 0);
    } else if (action === 'mem-letter') {
      const story = panelBody.dataset.memStory || '';
      window.DearlyLetters.mount(panelBody, { view: 'compose' });
      setTimeout(() => {
        const composeText = panelBody.querySelector('#composeText');
        if (composeText) composeText.value = story;
      }, 0);
    } else if (action === 'mem-timeline') {
      saveMemoryAsJournal('Timeline moment', 'Pinned to your timeline.');
    } else if (action === 'mem-archive') {
      saveMemoryAsJournal('Archived memory', 'Tucked away in your archives.');
    }
  });
})();
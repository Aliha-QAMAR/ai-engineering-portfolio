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

  async function mount(panelBody, opts) {
    opts = opts || {};
    panelBody.innerHTML = `
      <h3>Pen pals</h3>
      <p class="sub">No profiles, no messages — just an invitation, when you're ready</p>
      <div class="penpal-tabs">
        <button class="penpal-tab" data-tab="search">Find someone</button>
        <button class="penpal-tab" data-tab="incoming">Requests<span class="badge" id="incomingBadge" style="display:none;"></span></button>
        <button class="penpal-tab" data-tab="mine">My pen pals</button>
      </div>
      <div id="penpalTabBody"></div>
    `;
    panelBody.querySelectorAll('.penpal-tab').forEach(btn => {
      btn.addEventListener('click', () => renderTab(panelBody, btn.dataset.tab));
    });
    await refreshBadge(panelBody);
    renderTab(panelBody, opts.tab || 'search');
  }

  async function refreshBadge(panelBody) {
    try {
      const res = await apiRaw('/penpals/requests/incoming');
      const data = await res.json();
      const n = (data.requests || []).length;
      const badge = panelBody.querySelector('#incomingBadge');
      if (n > 0) { badge.textContent = n; badge.style.display = 'flex'; }
      else badge.style.display = 'none';
    } catch (e) { /* ignore */ }
  }

  function setActiveTab(panelBody, tab) {
    panelBody.querySelectorAll('.penpal-tab').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  }

  async function renderTab(panelBody, tab) {
    setActiveTab(panelBody, tab);
    const body = panelBody.querySelector('#penpalTabBody');
    if (tab === 'search') return renderSearch(body);
    if (tab === 'incoming') return renderIncoming(panelBody, body);
    if (tab === 'mine') return renderMine(body);
  }

  function renderSearch(body) {
    body.innerHTML = `
      <div class="search-row">
        <input type="text" id="ppSearch" placeholder="Search a username...">
        <button class="btn btn-secondary" id="ppSearchBtn">Search</button>
      </div>
      <div id="ppResults"></div>
    `;
    const input = body.querySelector('#ppSearch');
    const runSearch = async () => {
      const q = input.value.trim();
      const results = body.querySelector('#ppResults');
      if (q.length < 2) { results.innerHTML = `<p style="color:var(--ink-soft); font-style:italic;">Type at least 2 letters.</p>`; return; }
      results.innerHTML = `<p style="color:var(--ink-soft); font-style:italic;">Searching…</p>`;
      try {
        const res = await apiRaw('/penpals/search?q=' + encodeURIComponent(q));
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Search failed.');
        if (!data.results.length) {
          results.innerHTML = `<div class="empty-state"><p class="line">No one by that name here.</p></div>`;
          return;
        }
        results.innerHTML = data.results.map(r => `
          <div class="penpal-row">
            <span class="who">${escapeHtml(r.username)}</span>
            ${r.is_penpal ? `<span class="status-tag">Already pen pals</span>` :
              r.request_pending ? `<span class="status-tag">Request sent</span>` :
              `<button class="btn btn-secondary" data-send="${escapeHtml(r.username)}">Send request</button>`}
          </div>`).join('');
        results.querySelectorAll('[data-send]').forEach(btn => {
          btn.addEventListener('click', async () => {
            btn.disabled = true;
            try {
              const res2 = await apiRaw('/penpals/request', { method: 'POST', json: { to: btn.dataset.send } });
              const data2 = await res2.json();
              if (!res2.ok) throw new Error(data2.error || 'Could not send that request.');
              btn.outerHTML = `<span class="status-tag">Request sent</span>`;
            } catch (err) {
              alert(err.message);
              btn.disabled = false;
            }
          });
        });
      } catch (err) {
        results.innerHTML = `<div class="error-note show">${err.message}</div>`;
      }
    };
    body.querySelector('#ppSearchBtn').addEventListener('click', runSearch);
    input.addEventListener('keypress', e => { if (e.key === 'Enter') runSearch(); });
  }

  async function renderIncoming(panelBody, body) {
    body.innerHTML = `<p style="color:var(--ink-soft); font-style:italic;">Checking the door…</p>`;
    try {
      const res = await apiRaw('/penpals/requests/incoming');
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Could not load requests.');
      if (!data.requests.length) {
        body.innerHTML = `<div class="empty-state"><div class="glyph">🚪</div><p class="line">No one's knocking right now.</p></div>`;
        return;
      }
      body.innerHTML = data.requests.map(r => `
        <div class="penpal-row">
          <span class="who">${escapeHtml(r.from_username)}</span>
          <span>
            <button class="btn btn-secondary" data-accept="${r.id}" style="margin-right:.5rem;">Accept</button>
            <button class="btn btn-secondary" data-reject="${r.id}">Not now</button>
          </span>
        </div>`).join('');
      body.querySelectorAll('[data-accept]').forEach(btn => {
        btn.addEventListener('click', async () => {
          btn.disabled = true;
          try {
            const res2 = await apiRaw(`/penpals/requests/${btn.dataset.accept}/accept`, { method: 'POST', json: {} });
            if (!res2.ok) { const d = await res2.json(); throw new Error(d.error || 'Could not accept.'); }
            renderIncoming(panelBody, body);
            refreshBadge(panelBody);
          } catch (err) { alert(err.message); btn.disabled = false; }
        });
      });
      body.querySelectorAll('[data-reject]').forEach(btn => {
        btn.addEventListener('click', async () => {
          btn.disabled = true;
          try {
            const res2 = await apiRaw(`/penpals/requests/${btn.dataset.reject}/reject`, { method: 'POST', json: {} });
            if (!res2.ok) { const d = await res2.json(); throw new Error(d.error || 'Could not update that.'); }
            renderIncoming(panelBody, body);
            refreshBadge(panelBody);
          } catch (err) { alert(err.message); btn.disabled = false; }
        });
      });
    } catch (err) {
      body.innerHTML = `<div class="error-note show">${err.message}</div>`;
    }
  }

  async function renderMine(body) {
    body.innerHTML = `<p style="color:var(--ink-soft); font-style:italic;">Gathering names…</p>`;
    try {
      const res = await apiRaw('/penpals/mine');
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Could not load your pen pals.');
      if (!data.penpals.length) {
        body.innerHTML = `<div class="empty-state"><div class="glyph">🌍</div><p class="line">Your next friendship begins with your first letter.</p></div>`;
        return;
      }
      body.innerHTML = data.penpals.map(p => `
        <div class="penpal-row"><span class="who">${escapeHtml(p.username)}</span><span class="status-tag">Pen pals</span></div>
      `).join('');
    } catch (err) {
      body.innerHTML = `<div class="error-note show">${err.message}</div>`;
    }
  }

  window.DearlyPenpals = { mount };
})();

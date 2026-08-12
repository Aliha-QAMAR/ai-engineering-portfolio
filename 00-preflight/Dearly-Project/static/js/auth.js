(function () {
  const TOKEN_KEY = 'dearly_token';
  const USER_KEY = 'dearly_user';

  function getToken() { return localStorage.getItem(TOKEN_KEY); }
  function getUser() {
    try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null'); }
    catch (e) { return null; }
  }
  function setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  async function api(path, opts) {
    opts = opts || {};
    const headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
    const token = getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch('/api' + path, {
      method: opts.method || 'GET',
      headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Something went wrong.');
    return data;
  }

  function isSignedIn() { return !!getToken(); }

  // ---------- account pill ----------
  const acctStatus = document.getElementById('acctStatus');
  const acctAction = document.getElementById('acctAction');
  const acctAction2 = document.getElementById('acctAction2');
  const acctDivider2 = document.getElementById('acctDivider2');
  const musicToggleEl = document.getElementById('musicToggle');

  function refreshAcctPill() {
    const user = getUser();
    if (isSignedIn() && user) {
      acctStatus.textContent = user.username + "'s room";
      acctAction.textContent = 'Sign out';
      acctAction.dataset.action = 'signout';
      acctAction2.style.display = 'none';
      acctDivider2.style.display = 'none';
      musicToggleEl.style.display = 'flex';
    } else {
      acctStatus.textContent = 'Visiting as a guest';
      acctAction.textContent = 'Sign up';
      acctAction.dataset.action = 'signup';
      acctAction2.style.display = 'inline';
      acctDivider2.style.display = 'inline';
      musicToggleEl.style.display = 'none';
    }
  }

  function showAuthError(el, message) {
    el.textContent = message;
    el.classList.add('show');
  }
  function clearAuthError(el) {
    el.textContent = '';
    el.classList.remove('show');
  }

  // ---------- tab switching (with burn-in re-trigger) ----------
  const pageSignup = document.getElementById('pageSignup');
  const pageSignin = document.getElementById('pageSignin');
  const tabSignup = document.getElementById('tabSignup');
  const tabSignin = document.getElementById('tabSignin');

  function showAuthTab(name) {
    const showEl = name === 'signup' ? pageSignup : pageSignin;
    const hideEl = name === 'signup' ? pageSignin : pageSignup;
    hideEl.classList.add('hidden');
    showEl.classList.remove('hidden');
    tabSignup.classList.toggle('active', name === 'signup');
    tabSignin.classList.toggle('active', name === 'signin');
    // re-trigger the burn-in animation
    showEl.classList.remove('burn-in');
    void showEl.offsetWidth; // force reflow
    showEl.classList.add('burn-in');
  }

  document.querySelectorAll('[data-tab]').forEach(el => {
    el.addEventListener('click', () => showAuthTab(el.dataset.tab));
  });

  // ---------- forms ----------
  document.getElementById('formSignup').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('signupError');
    clearAuthError(errEl);
    const username = document.getElementById('signupUsername').value.trim();
    const password = document.getElementById('signupPassword').value;
    try {
      const data = await api('/auth/signup', { method: 'POST', body: { username, password } });
      setSession(data.token, data.user);
      refreshAcctPill();
      onSignedIn();
    } catch (err) {
      showAuthError(errEl, err.message);
    }
  });

  document.getElementById('formSignin').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('signinError');
    clearAuthError(errEl);
    const username = document.getElementById('signinUsername').value.trim();
    const password = document.getElementById('signinPassword').value;
    try {
      const data = await api('/auth/login', { method: 'POST', body: { username, password } });
      setSession(data.token, data.user);
      refreshAcctPill();
      onSignedIn();
    } catch (err) {
      showAuthError(errEl, err.message);
    }
  });

  function onSignedIn() {
    Router.goTo('dashboard');
    if (window.DearlyMusic) window.DearlyMusic.playOnEnter();
  }

  // ---------- pill buttons ----------
  acctAction.addEventListener('click', () => handlePillAction(acctAction.dataset.action));
  acctAction2.addEventListener('click', () => handlePillAction(acctAction2.dataset.action));

  async function handlePillAction(action) {
    if (action === 'signup' || action === 'signin') {
      Router.goTo('auth');
      showAuthTab(action);
    } else if (action === 'signout') {
      try { await api('/auth/logout', { method: 'POST' }); } catch (e) { /* ignore */ }
      clearSession();
      refreshAcctPill();
      if (window.DearlyMusic) window.DearlyMusic.stop();
      Router.goTo('landing', { replace: false });
      // reset history back to just landing
      while (Router.current() !== 'landing') Router.back();
    }
  }

  // ---------- "enter the writing room" ----------
  document.getElementById('scrollCue').addEventListener('click', () => {
    if (isSignedIn()) {
      Router.goTo('dashboard');
      if (window.DearlyMusic) window.DearlyMusic.playOnEnter();
    } else {
      Router.goTo('auth');
      showAuthTab('signup');
    }
  });

  // ---------- verify session on load ----------
  async function checkSession() {
    if (!getToken()) { refreshAcctPill(); return; }
    try {
      const data = await api('/auth/me');
      if (data.user) {
        localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      } else {
        clearSession();
      }
    } catch (e) {
      clearSession();
    }
    refreshAcctPill();
  }
  checkSession();

  window.DearlyAuth = { getToken, getUser, isSignedIn, api };
})();

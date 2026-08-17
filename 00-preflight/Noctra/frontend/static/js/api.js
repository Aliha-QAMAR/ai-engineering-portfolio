const API_BASE = '/api';

export const auth = {
  register(codename, password) {
    return fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ codename, password })
    }).then(res => {
      if (!res.ok) throw new Error('Registration failed. Check clearance protocols.');
      return res.json();
    });
  },
  login(codename, password) {
    return fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ codename, password })
    }).then(res => {
      if (!res.ok) throw new Error('Access denied. Invalid credentials.');
      return res.json();
    });
  },
  logout() {
    return fetch(`${API_BASE}/auth/logout`, { method: 'POST' });
  },
  status() {
    return fetch(`${API_BASE}/auth/status`).then(res => res.json());
  }
};

export const investigations = {
  create(caseName, description) {
    return fetch(`${API_BASE}/investigations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ caseName, description })
    }).then(res => res.json());
  },
  list() {
    return fetch(`${API_BASE}/investigations`).then(res => res.json());
  },
  get(id) {
    return fetch(`${API_BASE}/investigations/${id}`).then(res => res.json());
  },
  uploadEvidence(id, file) {
    const formData = new FormData();
    formData.append('evidence', file);
    return fetch(`${API_BASE}/investigations/${id}/evidence`, {
      method: 'POST',
      body: formData
    }).then(res => res.json());
  },
  investigate(id, onUpdate) {
    const source = new EventSource(`${API_BASE}/investigations/${id}/investigate`);
    source.onmessage = (event) => onUpdate(JSON.parse(event.data));
    return source;
  },
  report(id) {
    return fetch(`${API_BASE}/investigations/${id}/report`).then(res => res.json());
  }
};

export const memory = {
  list() {
    return fetch(`${API_BASE}/memory`).then(res => res.json());
  },
  store(key, value) {
    return fetch(`${API_BASE}/memory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value })
    }).then(res => res.json());
  }
};

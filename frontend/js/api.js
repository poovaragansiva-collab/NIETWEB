const API_BASE = 'https://college-tms.onrender.com/api';

const api = {
  async request(method, path, data = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (data) opts.body = JSON.stringify(data);

    const res = await fetch(`${API_BASE}${path}`, opts);
    const json = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(json.detail || `Request failed (${res.status})`);
    }
    return json;
  },
  get:    (path)       => api.request('GET',    path),
  post:   (path, data) => api.request('POST',   path, data),
  put:    (path, data) => api.request('PUT',    path, data),
  delete: (path)       => api.request('DELETE', path),
};

const BASE = '/api';

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok && res.headers.get('content-type')?.includes('application/json')) {
    const err = await res.json();
    throw new Error(err.error || `Error ${res.status}`);
  }
  if (res.headers.get('content-type')?.includes('application/json')) {
    return res.json();
  }
  return res;
}

export const api = {
  tareas: {
    list: (params = {}) => {
      const q = new URLSearchParams(params).toString();
      return request(`/tareas${q ? '?' + q : ''}`);
    },
    create: (data) => request('/tareas', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/tareas/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/tareas/${id}`, { method: 'DELETE' }),
    completar: (id, data) => request(`/tareas/${id}/completar`, { method: 'POST', body: JSON.stringify(data) }),
    addSub: (id, data) => request(`/tareas/${id}/sub`, { method: 'POST', body: JSON.stringify(data) }),
    toggleSub: (id, sid) => request(`/tareas/${id}/sub/${sid}/toggle`, { method: 'POST' }),
  },
  plan: {
    get: (tipo = 'todos') => request(`/plan?tipo=${tipo}`),
    export: (tipo = 'knapsack') => `${BASE}/plan/export?tipo=${tipo}`,
  },
  eisenhower: () => request('/eisenhower'),
  alertas: () => request('/alertas'),
  metricas: () => request('/metricas'),
  historial: () => request('/historial'),
  usuario: {
    get: () => request('/usuario'),
    update: (data) => request('/usuario', { method: 'PUT', body: JSON.stringify(data) }),
  },
  export: {
    tareas: () => `${BASE}/export/tareas`,
    historial: () => `${BASE}/export/historial`,
  },
};

const API_BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

export const floorsApi = {
  list: () => request("/floors"),
  create: (data) => request("/floors", {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/floors/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/floors/${id}`, { method: "DELETE" }),
};

export const widgetsApi = {
  list: (floorId) => request(`/floors/${floorId}/widgets`),
  create: (floorId, widgetType, config) =>
    request(`/floors/${floorId}/widgets`, {
      method: "POST",
      body: JSON.stringify({ floor_id: floorId, widget_type: widgetType, config }),
    }),
};

export const chatApi = {
  list: (floorId) => request(`/floors/${floorId}/chat`),
  send: (data) => request("/chat", {
    method: "POST",
    body: JSON.stringify(data),
  }),
};

export const widgetDataApi = {
  get: (widgetId) => request(`/widgets/${widgetId}/data`),
  set: (widgetId, payload) =>
    request(`/widgets/${widgetId}/data`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
};
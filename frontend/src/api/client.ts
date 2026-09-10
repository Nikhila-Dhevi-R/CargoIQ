const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '');

/**
 * Local development uses Vite's /api proxy. For a hosted build, set
 * VITE_API_BASE to the public FastAPI API URL (ending in /api).
 */
export const API_BASE = import.meta.env.VITE_API_BASE
  ? trimTrailingSlash(import.meta.env.VITE_API_BASE)
  : '/api';

/** Public FastAPI origin for video assets and WebSocket connections. */
export const BACKEND_BASE = import.meta.env.VITE_BACKEND_BASE
  ? trimTrailingSlash(import.meta.env.VITE_BACKEND_BASE)
  : API_BASE.startsWith('http')
    ? API_BASE.replace(/\/api$/, '')
    : '';

export const WEBSOCKET_BASE = import.meta.env.VITE_WS_BASE
  ? trimTrailingSlash(import.meta.env.VITE_WS_BASE)
  : BACKEND_BASE
    ? BACKEND_BASE.replace(/^http/, 'ws')
    : typeof window !== 'undefined'
      ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`
      : '';

export async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {})
    }
  });

  if (!res.ok) {
    let errMsg = `API Error (${res.status})`;
    try {
      const errJson = await res.json();
      errMsg = errJson.detail || errJson.message || errMsg;
    } catch {
      // ignore
    }
    throw new Error(errMsg);
  }

  const json = await res.json();
  if (json && typeof json === 'object' && 'success' in json && 'data' in json) {
    return json.data as T;
  }
  return json as T;
}

/**
 * API client with JWT auth and refresh token handling.
 * Uses VITE_API_BASE_URL for requests; refresh uses credentials (cookies).
 */

const API_PREFIX = '/api/v1';

function getBaseUrl(): string {
  const env = import.meta.env.VITE_API_BASE_URL as string | undefined;
  if (env) return env.replace(/\/$/, '');
  return '';
}

let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

async function refreshAccessToken(): Promise<boolean> {
  const base = getBaseUrl();
  const url = base ? `${base}${API_PREFIX}/auth/token/refresh` : `${API_PREFIX}/auth/token/refresh`;
  const res = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) return false;
  const data = await res.json();
  if (data?.access_token) {
    setAccessToken(data.access_token);
    return true;
  }
  return false;
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {}
): Promise<{ data?: T; error?: { status: number; body: unknown } }> {
  const base = getBaseUrl();
  const url = base ? `${base}${path}` : path;
  const headers = new Headers(init.headers);
  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }
  if (!headers.has('Content-Type') && init.body && typeof init.body === 'string') {
    headers.set('Content-Type', 'application/json');
  }
  let res = await fetch(url, { ...init, headers, credentials: 'include' });

  if (res.status === 401 && path !== `${API_PREFIX}/auth/token/refresh`) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers.set('Authorization', `Bearer ${getAccessToken()}`);
      res = await fetch(url, { ...init, headers, credentials: 'include' });
    }
  }

  if (!res.ok) {
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      body = await res.text();
    }
    return { error: { status: res.status, body } };
  }

  if (res.status === 204) {
    return {};
  }

  try {
    const data = (await res.json()) as T;
    return { data };
  } catch {
    return {};
  }
}

export function buildTaskListParams(params: {
  completed?: boolean | null;
  q?: string | null;
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}): string {
  const sp = new URLSearchParams();
  if (params.completed !== undefined && params.completed !== null) sp.set('completed', String(params.completed));
  if (params.q != null && params.q !== '') sp.set('q', params.q);
  if (params.skip != null) sp.set('skip', String(params.skip));
  if (params.limit != null) sp.set('limit', String(params.limit));
  if (params.sort_by) sp.set('sort_by', params.sort_by);
  if (params.sort_order) sp.set('sort_order', params.sort_order);
  const qs = sp.toString();
  return qs ? `?${qs}` : '';
}

export function buildUserListParams(params: {
  active?: boolean | null;
  q?: string | null;
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}): string {
  const sp = new URLSearchParams();
  if (params.active !== undefined && params.active !== null) sp.set('active', String(params.active));
  if (params.q != null && params.q !== '') sp.set('q', params.q);
  if (params.skip != null) sp.set('skip', String(params.skip));
  if (params.limit != null) sp.set('limit', String(params.limit));
  if (params.sort_by) sp.set('sort_by', params.sort_by);
  if (params.sort_order) sp.set('sort_order', params.sort_order);
  const qs = sp.toString();
  return qs ? `?${qs}` : '';
}

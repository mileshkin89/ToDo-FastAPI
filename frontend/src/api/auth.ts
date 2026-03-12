import type { Token, UserCreate, UserResponse, ChangePassword, ResetPasswordRequest, ResetPasswordConfirm } from './types';
import { apiFetch, setAccessToken } from './client';

const AUTH = '/api/v1/auth';

/**
 * Decode JWT payload without verification (client-side only; used to read sub after login).
 * Verification is done by the API when the token is sent.
 */
export function decodeJwtPayload(accessToken: string): { sub?: string } | null {
  try {
    const parts = accessToken.split('.');
    if (parts.length !== 3) return null;
    const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const decoded = atob(payload);
    return JSON.parse(decoded) as { sub?: string };
  } catch {
    return null;
  }
}

export async function login(username: string, password: string): Promise<{ data?: Token; error?: { status: number; body: unknown } }> {
  const body = new URLSearchParams();
  body.set('username', username);
  body.set('password', password);
  body.set('grant_type', 'password');
  const result = await apiFetch<Token>(`${AUTH}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });
  if (result.data) setAccessToken(result.data.access_token);
  return result;
}

export async function register(payload: UserCreate): Promise<{ data?: UserResponse; error?: { status: number; body: unknown } }> {
  return apiFetch<UserResponse>(`${AUTH}/register`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function logout(): Promise<{ error?: { status: number; body: unknown } }> {
  const result = await apiFetch<unknown>(`${AUTH}/logout`, { method: 'POST' });
  setAccessToken(null);
  return result;
}

export async function changePassword(payload: ChangePassword): Promise<{ error?: { status: number; body: unknown } }> {
  return apiFetch<unknown>(`${AUTH}/change_password`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function resetPasswordRequest(payload: ResetPasswordRequest): Promise<{ error?: { status: number; body: unknown } }> {
  return apiFetch<unknown>(`${AUTH}/reset_password/request`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function resetPasswordConfirm(payload: ResetPasswordConfirm): Promise<{ error?: { status: number; body: unknown } }> {
  return apiFetch<unknown>(`${AUTH}/reset_password/confirm`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export interface ProtectedUser {
  user_id: number;
  user_email: string;
  is_superuser: boolean;
}

export async function getCurrentUser(): Promise<{
  data?: ProtectedUser;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<ProtectedUser>('/protected');
}

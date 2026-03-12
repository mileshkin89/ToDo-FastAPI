import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { getCurrentUser, login as apiLogin, logout as apiLogout } from '../api/auth';
import { setAccessToken } from '../api/client';

interface User {
  id: number;
  email: string;
  is_superuser: boolean;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  checked: boolean;
}

interface AuthContextValue extends AuthState {
  login: (username: string, password: string) => Promise<{ ok: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function formatError(err: { status: number; body: unknown }): string {
  if (err.status === 401) return 'Invalid email or password.';
  if (typeof err.body === 'object' && err.body !== null && 'detail' in err.body) {
    const d = (err.body as { detail: unknown }).detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) return (d as { msg?: string }[]).map((x) => x.msg || '').filter(Boolean).join(' ') || 'Validation error';
  }
  return 'Request failed.';
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({ user: null, loading: false, checked: false });

  const refreshUser = useCallback(async () => {
    const result = await getCurrentUser();
    if (result.data) {
      setState((s) => ({ ...s, user: { id: result.data!.user_id, email: result.data!.user_email, is_superuser: result.data!.is_superuser }, checked: true }));
    } else {
      setAccessToken(null);
      setState((s) => ({ ...s, user: null, checked: true }));
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = useCallback(
    async (username: string, password: string): Promise<{ ok: boolean; error?: string }> => {
      setState((s) => ({ ...s, loading: true }));
      const result = await apiLogin(username, password);
      setState((s) => ({ ...s, loading: false }));
      if (result.data) {
        await refreshUser();
        return { ok: true };
      }
      return { ok: false, error: result.error ? formatError(result.error) : 'Login failed.' };
    },
    [refreshUser]
  );

  const logout = useCallback(async () => {
    await apiLogout();
    setState({ user: null, loading: false, checked: true });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      login,
      logout,
      refreshUser,
    }),
    [state, login, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

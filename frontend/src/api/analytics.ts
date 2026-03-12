import type { AnalyticsPeriod } from './types';
import { apiFetch } from './client';

const ANALYTICS = '/api/v1/analytics';

export async function userAnalytics(): Promise<{
  data?: Record<string, unknown>;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<Record<string, unknown>>(`${ANALYTICS}/users_global`);
}

export async function userAnalyticsAggregated(period: AnalyticsPeriod = '7d'): Promise<{
  data?: Record<string, unknown>;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<Record<string, unknown>>(`${ANALYTICS}/users_aggregated?period=${period}`);
}

export async function globalAnalytics(): Promise<{
  data?: Record<string, unknown>;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<Record<string, unknown>>(`${ANALYTICS}/global`);
}

export async function globalAnalyticsAggregated(period: AnalyticsPeriod = '7d'): Promise<{
  data?: Record<string, unknown>;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<Record<string, unknown>>(`${ANALYTICS}/global_aggregated?period=${period}`);
}

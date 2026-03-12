import type { UserResponse, UserListResponse, TaskByUserResponse } from './types';
import { apiFetch, buildUserListParams, buildTaskListParams } from './client';

const ADMIN = '/api/v1/admin/users';

export interface UserListParams {
  active?: boolean | null;
  q?: string | null;
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export async function adminUserList(params: UserListParams = {}): Promise<{
  data?: UserListResponse;
  error?: { status: number; body: unknown };
}> {
  const qs = buildUserListParams(params);
  return apiFetch<UserListResponse>(`${ADMIN}${qs}`);
}

export async function adminUserGet(userId: number): Promise<{
  data?: UserResponse;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<UserResponse>(`${ADMIN}/${userId}`);
}

export async function adminUserActivate(userId: number): Promise<{
  data?: UserResponse;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<UserResponse>(`${ADMIN}/${userId}/activate`, { method: 'PATCH' });
}

export async function adminUserDeactivate(userId: number): Promise<{
  data?: UserResponse;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<UserResponse>(`${ADMIN}/${userId}/deactivate`, { method: 'PATCH' });
}

export interface UserTasksParams {
  completed?: boolean | null;
  q?: string | null;
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export async function adminUserTasks(
  userId: number,
  params: UserTasksParams = {}
): Promise<{
  data?: TaskByUserResponse;
  error?: { status: number; body: unknown };
}> {
  const qs = buildTaskListParams(params);
  return apiFetch<TaskByUserResponse>(`${ADMIN}/${userId}/tasks${qs}`);
}

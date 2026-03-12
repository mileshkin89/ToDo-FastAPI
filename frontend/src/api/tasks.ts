import type { TaskResponse, TaskListResponse, TaskCreate, TaskUpdate } from './types';
import { apiFetch, buildTaskListParams } from './client';

const TASKS = '/api/v1/tasks';

export interface TaskListParams {
  completed?: boolean | null;
  q?: string | null;
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export async function taskList(params: TaskListParams = {}): Promise<{
  data?: TaskListResponse;
  error?: { status: number; body: unknown };
}> {
  const qs = buildTaskListParams(params);
  return apiFetch<TaskListResponse>(`${TASKS}${qs}`);
}

export async function taskGet(taskId: number): Promise<{
  data?: TaskResponse;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<TaskResponse>(`${TASKS}/${taskId}`);
}

export async function taskCreate(payload: TaskCreate): Promise<{
  data?: TaskResponse;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<TaskResponse>(`${TASKS}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function taskUpdate(taskId: number, payload: TaskUpdate): Promise<{
  data?: TaskResponse;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<TaskResponse>(`${TASKS}/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export async function taskDelete(taskId: number): Promise<{
  error?: { status: number; body: unknown };
}> {
  return apiFetch<unknown>(`${TASKS}/${taskId}`, { method: 'DELETE' });
}

export async function taskToggle(taskId: number): Promise<{
  data?: TaskResponse;
  error?: { status: number; body: unknown };
}> {
  return apiFetch<TaskResponse>(`${TASKS}/${taskId}/toggle`, { method: 'PATCH' });
}

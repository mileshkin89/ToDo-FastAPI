/**
 * API types aligned with OpenAPI schema (openapi.json).
 */

export interface UserResponse {
  id: number;
  email: string;
  name: string | null;
  is_active: boolean;
  last_login: string | null;
}

export interface UserCreate {
  email: string;
  name?: string | null;
  password: string;
  repeat_password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface TaskResponse {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
  start_at: string | null;
  completed_at: string | null;
  due_date: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  completed?: boolean;
  start_at?: string | null;
  due_date?: string | null;
}

export interface TaskUpdate {
  title?: string | null;
  description?: string | null;
  start_at?: string | null;
  due_date?: string | null;
}

export interface PaginationMeta {
  total?: number;
  skip?: number;
  limit?: number;
  has_more?: boolean;
}

export interface TaskListResponse {
  tasks: TaskResponse[];
  pagination?: PaginationMeta | null;
}

export interface UserListResponse {
  users: UserResponse[];
  pagination?: PaginationMeta | null;
}

export interface TaskByUserResponse {
  user: UserResponse;
  tasks: TaskResponse[];
  pagination?: PaginationMeta | null;
}

export interface ChangePassword {
  current_password: string;
  new_password: string;
  repeat_new_password: string;
}

export interface ResetPasswordRequest {
  email: string;
}

export interface ResetPasswordConfirm {
  token: string;
  new_password: string;
  repeat_new_password: string;
}

export type AnalyticsPeriod = '24h' | '7d' | '4w';

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
  input?: unknown;
  ctx?: Record<string, unknown>;
}

export interface HTTPValidationError {
  detail: ValidationError[];
}

import { useCallback, useEffect, useState } from 'react';
import { adminUserList, adminUserTasks, adminUserActivate, adminUserDeactivate } from '../api/admin';
import type { UserResponse, TaskResponse } from '../api/types';
import { Header } from '../components/Header';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import styles from './AdminPage.module.css';

const LIMIT = 10;

function formatDate(s: string | null): string {
  if (!s) return '—';
  try {
    return new Date(s).toLocaleString();
  } catch {
    return '—';
  }
}

export function AdminPage() {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [pagination, setPagination] = useState<{ total?: number; has_more?: boolean } | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null);
  const [userTasks, setUserTasks] = useState<TaskResponse[]>([]);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError('');
    const result = await adminUserList({
      skip: page * LIMIT,
      limit: LIMIT,
      q: search || undefined,
      sort_by: 'id',
      sort_order: 'desc',
    });
    setLoading(false);
    if (result.error) {
      if (result.error.status === 403) setError('Access denied. Admin only.');
      else setError('Failed to load users.');
      setUsers([]);
      return;
    }
    if (result.data) {
      setUsers(result.data.users);
      setPagination(result.data.pagination ?? null);
    }
  }, [page, search]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  useEffect(() => {
    if (!selectedUser) {
      setUserTasks([]);
      return;
    }
    setTasksLoading(true);
    adminUserTasks(selectedUser.id, { limit: 50 })
      .then((res) => {
        if (res.data) setUserTasks(res.data.tasks);
        else setUserTasks([]);
      })
      .finally(() => setTasksLoading(false));
  }, [selectedUser]);

  async function handleActivate(user: UserResponse) {
    const result = await adminUserActivate(user.id);
    if (result.data) fetchUsers();
    if (selectedUser?.id === user.id) setSelectedUser(result.data ?? selectedUser);
  }

  async function handleDeactivate(user: UserResponse) {
    const result = await adminUserDeactivate(user.id);
    if (result.data) fetchUsers();
    if (selectedUser?.id === user.id) setSelectedUser(result.data ?? selectedUser);
  }

  const total = pagination?.total ?? 0;
  const hasMore = pagination?.has_more ?? false;

  return (
    <>
      <Header title="Admin · Users" />
      {error && <div className={styles.errorBanner}>{error}</div>}

      <div className={styles.toolbar}>
        <Input
          placeholder="Search by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && setPage(0)}
          className={styles.search}
        />
      </div>

      {loading ? (
        <p className={styles.status}>Loading...</p>
      ) : (
        <div className={styles.layout}>
          <div className={styles.userList}>
            <Card>
              <ul className={styles.ul}>
                {users.map((u) => (
                  <li
                    key={u.id}
                    className={selectedUser?.id === u.id ? `${styles.userRow} ${styles.selected}` : styles.userRow}
                    onClick={() => setSelectedUser(u)}
                  >
                    <span className={styles.userEmail}>{u.email}</span>
                    <span className={u.is_active ? styles.badgeActive : styles.badgeInactive}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </li>
                ))}
              </ul>
            </Card>
            {total > LIMIT && (
              <div className={styles.pagination}>
                <Button variant="secondary" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
                  Previous
                </Button>
                <span className={styles.pageInfo}>Page {page + 1} · {total} total</span>
                <Button variant="secondary" disabled={!hasMore} onClick={() => setPage((p) => p + 1)}>
                  Next
                </Button>
              </div>
            )}
          </div>
          <div className={styles.detail}>
            {selectedUser ? (
              <Card>
                <h3 className={styles.detailTitle}>{selectedUser.email}</h3>
                <p className={styles.meta}>ID: {selectedUser.id} · Name: {selectedUser.name ?? '—'}</p>
                <p className={styles.meta}>Last login: {formatDate(selectedUser.last_login)}</p>
                <div className={styles.actions}>
                  {selectedUser.is_active ? (
                    <Button variant="danger" onClick={() => handleDeactivate(selectedUser)}>
                      Deactivate
                    </Button>
                  ) : (
                    <Button onClick={() => handleActivate(selectedUser)}>
                      Activate
                    </Button>
                  )}
                </div>
                <h4 className={styles.tasksTitle}>Tasks</h4>
                {tasksLoading ? (
                  <p className={styles.status}>Loading tasks...</p>
                ) : userTasks.length === 0 ? (
                  <p className={styles.status}>No tasks.</p>
                ) : (
                  <ul className={styles.taskList}>
                    {userTasks.map((t) => (
                      <li key={t.id} className={styles.taskItem}>
                        <span className={t.completed ? styles.taskDone : ''}>{t.title}</span>
                        <span className={styles.taskMeta}>Due: {formatDate(t.due_date)}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            ) : (
              <Card>
                <p className={styles.status}>Select a user</p>
              </Card>
            )}
          </div>
        </div>
      )}
    </>
  );
}

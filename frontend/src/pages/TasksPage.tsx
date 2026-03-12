import React, { useCallback, useEffect, useState } from 'react';
import {
  taskList,
  taskCreate,
  taskUpdate,
  taskDelete,
  taskToggle,
  type TaskListParams,
} from '../api/tasks';
import type { TaskResponse, TaskCreate as TaskCreateType, TaskUpdate as TaskUpdateType } from '../api/types';
import { Header } from '../components/Header';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Modal } from '../components/Modal';
import { Card } from '../components/Card';
import styles from './TasksPage.module.css';

const LIMIT = 10;

function formatDate(s: string | null): string {
  if (!s) return '—';
  try {
    const d = new Date(s);
    return d.toLocaleDateString(undefined, { dateStyle: 'short' });
  } catch {
    return '—';
  }
}

export function TasksPage() {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [pagination, setPagination] = useState<{ total?: number; skip?: number; limit?: number; has_more?: boolean } | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [search, setSearch] = useState('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(0);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskResponse | null>(null);
  const [formTitle, setFormTitle] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formDueDate, setFormDueDate] = useState('');
  const [submitLoading, setSubmitLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    const params: TaskListParams = {
      skip: page * LIMIT,
      limit: LIMIT,
      sort_by: 'created_at',
      sort_order: sortOrder,
      q: search || undefined,
    };
    if (filter === 'active') params.completed = false;
    if (filter === 'completed') params.completed = true;
    const result = await taskList(params);
    setLoading(false);
    if (result.data) {
      setTasks(result.data.tasks);
      setPagination(result.data.pagination ?? null);
    } else {
      setTasks([]);
    }
  }, [page, filter, search, sortOrder]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  function openCreate() {
    setEditingTask(null);
    setFormTitle('');
    setFormDescription('');
    setFormDueDate('');
    setError('');
    setModalOpen(true);
  }

  function openEdit(task: TaskResponse) {
    setEditingTask(task);
    setFormTitle(task.title);
    setFormDescription(task.description ?? '');
    setFormDueDate(task.due_date ? task.due_date.slice(0, 16) : '');
    setError('');
    setModalOpen(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (!formTitle.trim()) {
      setError('Title is required.');
      return;
    }
    setSubmitLoading(true);
    if (editingTask) {
      const payload: TaskUpdateType = {
        title: formTitle.trim(),
        description: formDescription.trim() || null,
        due_date: formDueDate ? new Date(formDueDate).toISOString() : null,
      };
      const result = await taskUpdate(editingTask.id, payload);
      setSubmitLoading(false);
      if (result.error) {
        setError('Update failed.');
        return;
      }
      setModalOpen(false);
      fetchTasks();
    } else {
      const payload: TaskCreateType = {
        title: formTitle.trim(),
        description: formDescription.trim() || null,
        due_date: formDueDate ? new Date(formDueDate).toISOString() : null,
      };
      const result = await taskCreate(payload);
      setSubmitLoading(false);
      if (result.error) {
        setError('Create failed.');
        return;
      }
      setModalOpen(false);
      fetchTasks();
    }
  }

  async function handleToggle(task: TaskResponse) {
    const result = await taskToggle(task.id);
    if (result.data) setTasks((prev) => prev.map((t) => (t.id === task.id ? result.data! : t)));
    else fetchTasks();
  }

  async function handleDelete(task: TaskResponse) {
    if (!window.confirm('Delete this task?')) return;
    const result = await taskDelete(task.id);
    if (!result.error) fetchTasks();
  }

  const total = pagination?.total ?? 0;
  const hasMore = pagination?.has_more ?? false;

  return (
    <>
      <Header
        title="My Tasks"
        children={
          <Button onClick={openCreate}>Add task</Button>
        }
      />

      <div className={styles.toolbar}>
        <Input
          placeholder="Search tasks..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && setPage(0)}
          className={styles.search}
        />
        <div className={styles.filters}>
          {(['all', 'active', 'completed'] as const).map((f) => (
            <button
              key={f}
              type="button"
              className={filter === f ? styles.filterActive : styles.filterBtn}
              onClick={() => { setFilter(f); setPage(0); }}
            >
              {f === 'all' ? 'All' : f === 'active' ? 'Active' : 'Completed'}
            </button>
          ))}
        </div>
        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
          className={styles.sort}
        >
          <option value="desc">Newest first</option>
          <option value="asc">Oldest first</option>
        </select>
      </div>

      {loading ? (
        <p className={styles.status}>Loading...</p>
      ) : tasks.length === 0 ? (
        <Card>
          <p className={styles.empty}>No tasks yet. Add one above.</p>
        </Card>
      ) : (
        <ul className={styles.list}>
          {tasks.map((task) => (
            <li key={task.id} className={styles.taskRow}>
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => handleToggle(task)}
                className={styles.checkbox}
                aria-label="Toggle completion"
              />
              <div className={styles.taskBody}>
                <span className={task.completed ? styles.taskTitleDone : styles.taskTitle}>{task.title}</span>
                {task.description && <span className={styles.taskDesc}>{task.description}</span>}
                <span className={styles.taskMeta}>
                  Due: {formatDate(task.due_date)} · {task.completed_at ? `Done ${formatDate(task.completed_at)}` : 'In progress'}
                </span>
              </div>
              <div className={styles.taskActions}>
                <button type="button" className={styles.actionBtn} onClick={() => openEdit(task)}>
                  Edit
                </button>
                <button type="button" className={styles.actionBtnDanger} onClick={() => handleDelete(task)}>
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {total > LIMIT && (
        <div className={styles.pagination}>
          <Button
            variant="secondary"
            disabled={page === 0}
            onClick={() => setPage((p) => p - 1)}
          >
            Previous
          </Button>
          <span className={styles.pageInfo}>
            Page {page + 1} · {total} total
          </span>
          <Button
            variant="secondary"
            disabled={!hasMore}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingTask ? 'Edit task' : 'New task'}
      >
        <form onSubmit={handleSubmit}>
          {error && <div className={styles.errorBanner}>{error}</div>}
          <Input
            label="Title"
            value={formTitle}
            onChange={(e) => setFormTitle(e.target.value)}
            required
            maxLength={150}
            placeholder="Task title"
          />
          <div className={styles.formGroup}>
            <label className={styles.label}>Description (optional)</label>
            <textarea
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              maxLength={500}
              placeholder="Description"
              className={styles.textarea}
              rows={3}
            />
          </div>
          <Input
            type="datetime-local"
            label="Due date (optional)"
            value={formDueDate}
            onChange={(e) => setFormDueDate(e.target.value)}
          />
          <div className={styles.modalActions}>
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={submitLoading}>
              {editingTask ? 'Save' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </>
  );
}

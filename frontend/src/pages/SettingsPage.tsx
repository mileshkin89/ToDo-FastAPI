import React, { useState } from 'react';
import { changePassword } from '../api/auth';
import { Header } from '../components/Header';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import styles from './SettingsPage.module.css';

function formatError(err: { status: number; body: unknown }): string {
  if (typeof err.body === 'object' && err.body !== null && 'detail' in err.body) {
    const d = (err.body as { detail: unknown }).detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) return (d as { msg?: string }[]).map((x) => x.msg || '').filter(Boolean).join(' ') || 'Validation error';
  }
  return 'Failed to change password.';
}

export function SettingsPage() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setSuccess(false);
    if (newPassword.length < 5) {
      setError('New password must be at least 5 characters.');
      return;
    }
    if (newPassword !== repeatPassword) {
      setError('New passwords do not match.');
      return;
    }
    setLoading(true);
    const result = await changePassword({
      current_password: currentPassword,
      new_password: newPassword,
      repeat_new_password: repeatPassword,
    });
    setLoading(false);
    if (result.error) {
      setError(formatError(result.error));
      return;
    }
    setSuccess(true);
    setCurrentPassword('');
    setNewPassword('');
    setRepeatPassword('');
  }

  return (
    <>
      <Header title="Settings" />
      <Card>
        <h2 className={styles.sectionTitle}>Change password</h2>
        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.errorBanner}>{error}</div>}
          {success && <div className={styles.successBanner}>Password updated successfully.</div>}
          <Input
            type="password"
            label="Current password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
          <Input
            type="password"
            label="New password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            minLength={5}
            autoComplete="new-password"
          />
          <Input
            type="password"
            label="Repeat new password"
            value={repeatPassword}
            onChange={(e) => setRepeatPassword(e.target.value)}
            required
            autoComplete="new-password"
          />
          <Button type="submit" loading={loading}>
            Update password
          </Button>
        </form>
      </Card>
    </>
  );
}

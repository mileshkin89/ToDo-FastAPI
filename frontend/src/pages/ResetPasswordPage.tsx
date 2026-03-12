import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { resetPasswordConfirm } from '../api/auth';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import styles from './AuthPages.module.css';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [newPassword, setNewPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (newPassword.length < 5) {
      setError('Password must be at least 5 characters.');
      return;
    }
    if (newPassword !== repeatPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (!token) {
      setError('Missing reset token. Use the link from your email.');
      return;
    }
    setLoading(true);
    const result = await resetPasswordConfirm({
      token,
      new_password: newPassword,
      repeat_new_password: repeatPassword,
    });
    setLoading(false);
    if (result.error) {
      const body = result.error.body as { detail?: string } | undefined;
      setError(typeof body?.detail === 'string' ? body.detail : 'Reset failed. Token may be expired.');
      return;
    }
    setSuccess(true);
  }

  if (!token) {
    return (
      <>
        <h1 className={styles.title}>Invalid link</h1>
        <p className={styles.subtitle}>This reset link is invalid or missing the token. Please request a new link.</p>
        <Link to="/forgot-password" className={styles.link} style={{ display: 'block', textAlign: 'center', marginTop: 16 }}>
          Request new link
        </Link>
      </>
    );
  }

  if (success) {
    return (
      <>
        <h1 className={styles.title}>Password updated</h1>
        <p className={styles.subtitle}>You can now sign in with your new password.</p>
        <Link to="/login" className={styles.link} style={{ display: 'block', textAlign: 'center', marginTop: 16 }}>
          Sign in
        </Link>
      </>
    );
  }

  return (
    <>
      <h1 className={styles.title}>Set new password</h1>
      <p className={styles.subtitle}>Enter your new password below</p>
      <form onSubmit={handleSubmit} className={styles.form}>
        {error && <div className={styles.errorBanner}>{error}</div>}
        <Input
          type="password"
          label="New password"
          placeholder="At least 5 characters"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
          minLength={5}
          autoComplete="new-password"
        />
        <Input
          type="password"
          label="Repeat password"
          placeholder="Repeat new password"
          value={repeatPassword}
          onChange={(e) => setRepeatPassword(e.target.value)}
          required
          autoComplete="new-password"
        />
        <div className={styles.actions}>
          <Button type="submit" fullWidth loading={loading}>
            Reset password
          </Button>
        </div>
      </form>
    </>
  );
}

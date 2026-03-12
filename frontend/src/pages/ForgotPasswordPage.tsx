import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { resetPasswordRequest } from '../api/auth';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import styles from './AuthPages.module.css';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    const result = await resetPasswordRequest({ email: email.trim() });
    setLoading(false);
    if (result.error) {
      setError('Request failed. Please try again.');
      return;
    }
    setSent(true);
  }

  if (sent) {
    return (
      <>
        <h1 className={styles.title}>Check your email</h1>
        <p className={styles.subtitle}>
          If an account exists for {email}, we&apos;ve sent a password reset link.
        </p>
        <Link to="/login" className={styles.link} style={{ display: 'block', textAlign: 'center', marginTop: 16 }}>
          Back to sign in
        </Link>
      </>
    );
  }

  return (
    <>
      <h1 className={styles.title}>Forgot password</h1>
      <p className={styles.subtitle}>Enter your email to receive a reset link</p>
      <form onSubmit={handleSubmit} className={styles.form}>
        {error && <div className={styles.errorBanner}>{error}</div>}
        <Input
          type="email"
          label="Email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />
        <div className={styles.actions}>
          <Button type="submit" fullWidth loading={loading}>
            Send reset link
          </Button>
          <Link to="/login" className={styles.link}>
            Back to sign in
          </Link>
        </div>
      </form>
    </>
  );
}

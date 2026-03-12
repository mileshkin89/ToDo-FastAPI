import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import styles from './AuthPages.module.css';

export function LoginPage() {
  const navigate = useNavigate();
  const { login, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    const result = await login(email.trim(), password);
    if (result.ok) navigate('/tasks', { replace: true });
    else setError(result.error ?? 'Login failed');
  }

  return (
    <>
      <h1 className={styles.title}>Sign in</h1>
      <p className={styles.subtitle}>Enter your credentials to access your tasks</p>
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
        <Input
          type="password"
          label="Password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
        />
        <div className={styles.actions}>
          <Button type="submit" fullWidth loading={loading}>
            Sign in
          </Button>
          <Link to="/forgot-password" className={styles.link}>
            Forgot password?
          </Link>
        </div>
      </form>
      <p className={styles.footer}>
        Don&apos;t have an account? <Link to="/register">Sign up</Link>
      </p>
    </>
  );
}

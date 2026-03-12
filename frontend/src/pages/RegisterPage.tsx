import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api/auth';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import styles from './AuthPages.module.css';

function formatError(err: { status: number; body: unknown }): string {
  if (typeof err.body === 'object' && err.body !== null && 'detail' in err.body) {
    const d = (err.body as { detail: unknown }).detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) return (d as { msg?: string }[]).map((x) => x.msg || '').filter(Boolean).join(' ') || 'Validation error';
  }
  return 'Registration failed.';
}

export function RegisterPage() {
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (password !== repeatPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 5) {
      setError('Password must be at least 5 characters.');
      return;
    }
    setLoading(true);
    const result = await register({ email: email.trim(), name: name.trim() || null, password, repeat_password: repeatPassword });
    setLoading(false);
    if (result.data) {
      const loginRes = await authLogin(email.trim(), password);
      if (loginRes.ok) navigate('/tasks', { replace: true });
      else navigate('/login', { replace: true });
      return;
    }
    setError(result.error ? formatError(result.error) : 'Registration failed.');
  }

  return (
    <>
      <h1 className={styles.title}>Create account</h1>
      <p className={styles.subtitle}>Sign up to start managing your tasks</p>
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
          type="text"
          label="Name (optional)"
          placeholder="Your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoComplete="name"
        />
        <Input
          type="password"
          label="Password"
          placeholder="At least 5 characters"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={5}
          autoComplete="new-password"
        />
        <Input
          type="password"
          label="Repeat password"
          placeholder="Repeat password"
          value={repeatPassword}
          onChange={(e) => setRepeatPassword(e.target.value)}
          required
          autoComplete="new-password"
        />
        <div className={styles.actions}>
          <Button type="submit" fullWidth loading={loading}>
            Sign up
          </Button>
        </div>
      </form>
      <p className={styles.footer}>
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </>
  );
}

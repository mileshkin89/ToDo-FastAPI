import React from 'react';
import styles from './Input.module.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, id, className = '', ...rest }: InputProps) {
  const inputId = id ?? `input-${Math.random().toString(36).slice(2, 9)}`;
  return (
    <div className={styles.wrapper}>
      {label && (
        <label htmlFor={inputId} className={styles.label}>
          {label}
        </label>
      )}
      <input id={inputId} className={`${styles.input} ${error ? styles.hasError : ''} ${className}`} {...rest} />
      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
}

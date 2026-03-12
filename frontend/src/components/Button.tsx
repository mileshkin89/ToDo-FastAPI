import React from 'react';
import styles from './Button.module.css';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
  fullWidth?: boolean;
}

export function Button({
  variant = 'primary',
  loading = false,
  fullWidth,
  className = '',
  disabled,
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      type="button"
      className={`${styles.btn} ${styles[variant]} ${fullWidth ? styles.fullWidth : ''} ${className}`}
      disabled={disabled ?? loading}
      {...rest}
    >
      {loading ? <span className={styles.spinner} /> : children}
    </button>
  );
}

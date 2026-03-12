import React from 'react';
import styles from './Header.module.css';

interface HeaderProps {
  title: string;
  children?: React.ReactNode;
}

export function Header({ title, children }: HeaderProps) {
  return (
    <header className={styles.header}>
      <h1 className={styles.title}>{title}</h1>
      {children && <div className={styles.actions}>{children}</div>}
    </header>
  );
}

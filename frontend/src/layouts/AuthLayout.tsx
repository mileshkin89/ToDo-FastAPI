import { Outlet } from 'react-router-dom';
import styles from './AuthLayout.module.css';

export function AuthLayout() {
  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <Outlet />
      </div>
    </div>
  );
}

import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import styles from './MainLayout.module.css';

export function MainLayout() {
  return (
    <div className={styles.wrapper}>
      <Sidebar />
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}

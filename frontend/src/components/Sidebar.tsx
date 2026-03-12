import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import styles from './Sidebar.module.css';

export function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <span className={styles.logoIcon}>✓</span>
        <span className={styles.logoText}>Smart ToDo</span>
      </div>
      <nav className={styles.nav}>
        <NavLink
          to="/tasks"
          className={({ isActive }) => (isActive ? `${styles.link} ${styles.active}` : styles.link)}
        >
          My Tasks
        </NavLink>
        <NavLink
          to="/analytics"
          className={({ isActive }) => (isActive ? `${styles.link} ${styles.active}` : styles.link)}
        >
          Analytics
        </NavLink>
        {user?.is_superuser && (
          <NavLink
            to="/admin"
            className={({ isActive }) => (isActive ? `${styles.link} ${styles.active}` : styles.link)}
          >
            Admin
          </NavLink>
        )}
        <NavLink
          to="/settings"
          className={({ isActive }) => (isActive ? `${styles.link} ${styles.active}` : styles.link)}
        >
          Settings
        </NavLink>
      </nav>
      <div className={styles.footer}>
        <span className={styles.userEmail} title={user?.email ?? ''}>
          {user?.email ?? ''}
        </span>
        <LogoutButton />
      </div>
    </aside>
  );
}

function LogoutButton() {
  const { logout } = useAuth();
  return (
    <button type="button" className={styles.logout} onClick={() => logout()}>
      Log out
    </button>
  );
}

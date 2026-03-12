import { useEffect, useState } from 'react';
import { userAnalytics, userAnalyticsAggregated } from '../api/analytics';
import { Header } from '../components/Header';
import { Card, CardHeader, CardTitle } from '../components/Card';
import styles from './AnalyticsPage.module.css';

type Period = '24h' | '7d' | '4w';

export function AnalyticsPage() {
  const [counters, setCounters] = useState<Record<string, number> | null>(null);
  const [aggregated, setAggregated] = useState<Record<string, unknown> | null>(null);
  const [period, setPeriod] = useState<Period>('7d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([userAnalytics(), userAnalyticsAggregated(period)])
      .then(([res1, res2]) => {
        if (cancelled) return;
        const d1 = res1.data as { counters?: Record<string, number> } | undefined;
        if (d1?.counters) setCounters(d1.counters);
        if (res2.data && typeof res2.data === 'object') setAggregated(res2.data as Record<string, unknown>);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [period]);

  if (loading && !counters) {
    return (
      <>
        <Header title="Analytics" />
        <p className={styles.status}>Loading...</p>
      </>
    );
  }

  const total = counters?.total_tasks ?? 0;
  const active = counters?.active_tasks ?? 0;
  const completed = counters?.completed_tasks ?? 0;
  const overdue = counters?.overdue_tasks ?? 0;
  const overduePct = counters?.overdue_percent ?? 0;

  return (
    <>
      <Header
        title="Analytics"
        children={
          <select value={period} onChange={(e) => setPeriod(e.target.value as Period)} className={styles.periodSelect}>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="4w">Last 4 weeks</option>
          </select>
        }
      />

      <div className={styles.grid}>
        <Card>
          <CardHeader>
            <CardTitle>Total tasks</CardTitle>
          </CardHeader>
          <p className={styles.number}>{total}</p>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Active</CardTitle>
          </CardHeader>
          <p className={styles.number}>{active}</p>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Completed</CardTitle>
          </CardHeader>
          <p className={styles.number}>{completed}</p>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Overdue</CardTitle>
          </CardHeader>
          <p className={styles.number}>{overdue}</p>
          {total > 0 && <p className={styles.sub}>{overduePct.toFixed(1)}% of total</p>}
        </Card>
      </div>

      {aggregated && Object.keys(aggregated).length > 0 && (
        <Card className={styles.aggregated}>
          <CardHeader>
            <CardTitle>Activity (period: {period})</CardTitle>
          </CardHeader>
          <pre className={styles.pre}>{JSON.stringify(aggregated, null, 2)}</pre>
        </Card>
      )}
    </>
  );
}

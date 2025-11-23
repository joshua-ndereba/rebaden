import React, { useEffect, useState } from 'react';
import Panel from './Panel';
import { fetchMetrics } from '../services/api';
import '../styles/global.css';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetchMetrics()
      .then((data) => {
        if (mounted) setMetrics(data);
      })
      .catch((err) => {
        if (mounted) setError(err.message || 'Failed to load metrics');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => (mounted = false);
  }, []);

  if (loading) return <div className="loading">Loading SIEM metrics...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard-grid">
      <Panel title="Events per Minute">
        <div className="metric large">{metrics.eventsPerMinute}</div>
        <small>Last 5 minutes</small>
      </Panel>

      <Panel title="Active Alerts">
        <div className="metric medium">{metrics.activeAlerts}</div>
        <ul className="list">
          {metrics.topAlerts.map((a, i) => (
            <li key={i}>{a.name} • {a.count}</li>
          ))}
        </ul>
      </Panel>

      <Panel title="Top Sources">
        <ol>
          {metrics.topSources.map((s, i) => (
            <li key={i}>{s.ip} ({s.events})</li>
          ))}
        </ol>
      </Panel>

      <Panel title="Recent Events">
        <table className="events-table">
          <thead>
            <tr><th>Time</th><th>Source</th><th>Event</th></tr>
          </thead>
          <tbody>
            {metrics.recentEvents.map((e, i) => (
              <tr key={i}><td>{e.time}</td><td>{e.source}</td><td>{e.message}</td></tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

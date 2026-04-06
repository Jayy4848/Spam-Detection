import React, { useState, useEffect } from 'react';
import { getStats } from '../services/api';

const CAT_COLORS = {
  spam: '#ef4444', promotion: '#f59e0b', otp: '#3b82f6',
  important: '#8b5cf6', personal: '#10b981',
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getStats()
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Stats error:', err);
        setError('Could not load statistics. Make sure the backend is running on port 8000.');
        setLoading(false);
      });
  }, []);

  if (loading) return (
    <div className="dashboard-page">
      <div className="analyzing-state">
        <div className="pulse-dot" /><div className="pulse-dot" /><div className="pulse-dot" />
        Loading dashboard...
      </div>
    </div>
  );

  if (error) return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Analytics Dashboard</h1>
      </div>
      <div className="error-alert">
        ⚠️ {error}
        <button
          onClick={() => { setError(''); setLoading(true); getStats().then(setStats).catch(() => setError('Still cannot connect. Is the backend running?')).finally(() => setLoading(false)); }}
          style={{ marginLeft: '1rem', padding: '0.25rem 0.75rem', borderRadius: '6px', border: '1px solid', cursor: 'pointer', fontSize: '0.8rem' }}
        >
          Retry
        </button>
      </div>
    </div>
  );

  const total = stats?.total_messages || 0;
  const spam = stats?.spam_count || 0;
  const phishing = stats?.phishing_count || 0;
  const safe = total - spam - phishing;
  const spamRate = total > 0 ? ((spam / total) * 100).toFixed(1) : 0;

  const catDist = stats?.category_distribution || [];
  const maxCat = Math.max(...catDist.map(c => c.count), 1);

  const trends = stats?.daily_trends || [];
  const maxTrend = Math.max(...trends.map(t => t.count), 1);

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Analytics Dashboard</h1>
        <p>Real-time insights from your SMS analysis history</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon purple">📊</div>
          <div className="stat-info">
            <div className="stat-num">{total}</div>
            <div className="stat-label">Total Analyzed</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon red">🚨</div>
          <div className="stat-info">
            <div className="stat-num">{spam}</div>
            <div className="stat-label">Spam Detected</div>
            <div className="stat-change up">{spamRate}% of total</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon yellow">🎣</div>
          <div className="stat-info">
            <div className="stat-num">{phishing}</div>
            <div className="stat-label">Phishing Attempts</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green">✅</div>
          <div className="stat-info">
            <div className="stat-num">{safe > 0 ? safe : 0}</div>
            <div className="stat-label">Safe Messages</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon blue">💬</div>
          <div className="stat-info">
            <div className="stat-num">{stats?.feedback_count || 0}</div>
            <div className="stat-label">User Feedback</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        {/* Category distribution */}
        <div className="chart-card">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">Category Breakdown</div>
              <div className="chart-card-sub">Distribution of message types</div>
            </div>
          </div>
          {catDist.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📭</div>
              <h3>No data yet</h3>
              <p>Analyze some messages to see the breakdown</p>
            </div>
          ) : (
            <div className="category-list">
              {catDist.map((cat, i) => (
                <div key={i} className="category-row">
                  <div className="category-dot" style={{ background: CAT_COLORS[cat.category] || '#6b7280' }} />
                  <span className="category-name">{cat.category}</span>
                  <div className="category-bar-wrap">
                    <div
                      className="category-bar-fill"
                      style={{
                        width: `${(cat.count / maxCat) * 100}%`,
                        background: CAT_COLORS[cat.category] || '#6b7280'
                      }}
                    />
                  </div>
                  <span className="category-pct">
                    {total > 0 ? ((cat.count / total) * 100).toFixed(0) : 0}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 7-day trend */}
        <div className="chart-card">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">7-Day Activity</div>
              <div className="chart-card-sub">Messages analyzed per day</div>
            </div>
          </div>
          {trends.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📈</div>
              <h3>No trend data</h3>
              <p>Data will appear after daily usage</p>
            </div>
          ) : (
            <div className="trend-bars">
              {trends.map((t, i) => (
                <div key={i} className="trend-col">
                  <span className="trend-val">{t.count}</span>
                  <div
                    className="trend-bar"
                    style={{ height: `${Math.max((t.count / maxTrend) * 80, 4)}px` }}
                  />
                  <span className="trend-day">
                    {new Date(t.date).toLocaleDateString('en', { weekday: 'short' })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Confidence by category */}
      {stats?.average_confidence && Object.keys(stats.average_confidence).length > 0 && (
        <div className="chart-card">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">Average Model Confidence by Category</div>
              <div className="chart-card-sub">How confident the AI is per message type</div>
            </div>
          </div>
          <div className="category-list" style={{ marginTop: '0.5rem' }}>
            {Object.entries(stats.average_confidence).map(([cat, conf]) => (
              <div key={cat} className="category-row">
                <div className="category-dot" style={{ background: CAT_COLORS[cat] || '#6b7280' }} />
                <span className="category-name">{cat}</span>
                <div className="category-bar-wrap">
                  <div
                    className="category-bar-fill"
                    style={{ width: `${(conf || 0) * 100}%`, background: CAT_COLORS[cat] || '#6b7280' }}
                  />
                </div>
                <span className="category-pct">{((conf || 0) * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

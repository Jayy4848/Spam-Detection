import React, { useState, useEffect } from 'react';
import { getStats, resetData, getModelInfo, getRecentMessages, deleteMessage } from '../services/api';

const CAT_COLORS = {
  spam: '#ef4444', promotion: '#f59e0b', otp: '#3b82f6',
  important: '#8b5cf6', personal: '#10b981',
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [resetting, setResetting] = useState(false);
  const [modelInfo, setModelInfo] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [filterCategory, setFilterCategory] = useState(null);
  const [filterRisk, setFilterRisk] = useState(null);
  const [viewingMessage, setViewingMessage] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const loadStats = () => {
    setLoading(true);
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
  };

  const handleReset = async () => {
    if (!window.confirm('⚠️ Are you sure you want to reset all data? This action cannot be undone!')) {
      return;
    }
    
    setResetting(true);
    try {
      await resetData();
      alert('✅ All data has been reset successfully!');
      loadStats(); // Reload stats
    } catch (err) {
      console.error('Reset error:', err);
      alert('❌ Failed to reset data. Please try again.');
    } finally {
      setResetting(false);
    }
  };

  const loadMessages = (category = null, risk = null) => {
    setMessagesLoading(true);
    getRecentMessages({ limit: 50, offset: 0, category, risk_level: risk })
      .then(data => {
        setMessages(data.messages || []);
        setMessagesLoading(false);
      })
      .catch(err => {
        console.error('Messages error:', err);
        setMessagesLoading(false);
      });
  };

  const handleDeleteMessage = async (id) => {
    if (!window.confirm('⚠️ Are you sure you want to delete this message?')) {
      return;
    }
    
    setDeletingId(id);
    try {
      // Call delete API endpoint using the API service
      await deleteMessage(id);
      
      // Remove from local state
      setMessages(messages.filter(msg => msg.id !== id));
      
      // Show success message
      alert('✅ Message deleted successfully!');
      
      // Reload stats to update counts
      loadStats();
    } catch (err) {
      console.error('Delete error:', err);
      alert('❌ Failed to delete message. Please try again.');
    } finally {
      setDeletingId(null);
    }
  };

  const handleViewMessage = (message) => {
    setViewingMessage(message);
  };

  const closeMessageView = () => {
    setViewingMessage(null);
  };

  useEffect(() => {
    loadStats();
    loadMessages();
    // Load model info
    getModelInfo()
      .then(data => setModelInfo(data))
      .catch(err => console.error('Failed to load model info:', err));
  }, []);

  useEffect(() => {
    loadMessages(filterCategory, filterRisk);
  }, [filterCategory, filterRisk]);

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
        <button 
          className="btn-reset-data" 
          onClick={handleReset}
          disabled={resetting || total === 0}
          title={total === 0 ? 'No data to reset' : 'Reset all analytics data'}
        >
          {resetting ? '🔄 Resetting...' : '🗑️ Reset Data'}
        </button>
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

      {/* Recent Messages Log */}
      <div className="messages-log-card">
        <div className="chart-card-header">
          <div>
            <div className="chart-card-title">📋 Recent Analyzed Messages</div>
            <div className="chart-card-sub">Complete history of all analyzed SMS messages</div>
          </div>
        </div>

        {/* Filters */}
        <div className="messages-filters">
          <div className="filter-group">
            <span className="filter-label">Category:</span>
            <div className="filter-buttons">
              <button 
                className={`filter-btn ${filterCategory === null ? 'active' : ''}`}
                onClick={() => setFilterCategory(null)}
              >
                All
              </button>
              {['spam', 'promotion', 'otp', 'important', 'personal'].map(cat => (
                <button
                  key={cat}
                  className={`filter-btn ${filterCategory === cat ? 'active' : ''}`}
                  onClick={() => setFilterCategory(cat)}
                >
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <div className="filter-group">
            <span className="filter-label">Risk:</span>
            <div className="filter-buttons">
              <button 
                className={`filter-btn ${filterRisk === null ? 'active' : ''}`}
                onClick={() => setFilterRisk(null)}
              >
                All
              </button>
              {['high', 'medium', 'low'].map(risk => (
                <button
                  key={risk}
                  className={`filter-btn ${filterRisk === risk ? 'active' : ''}`}
                  onClick={() => setFilterRisk(risk)}
                >
                  {risk.charAt(0).toUpperCase() + risk.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Messages Table */}
        {messagesLoading ? (
          <div className="analyzing-state" style={{ padding: '2rem' }}>
            <div className="pulse-dot" /><div className="pulse-dot" /><div className="pulse-dot" />
            Loading messages...
          </div>
        ) : messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📭</div>
            <h3>No messages found</h3>
            <p>Analyze some messages to see them here</p>
          </div>
        ) : (
          <div className="messages-table-wrapper">
            <table className="messages-table">
              <colgroup>
                <col style={{ width: '140px' }} />
                <col style={{ width: '120px' }} />
                <col style={{ width: '160px' }} />
                <col style={{ width: '120px' }} />
                <col style={{ width: '120px' }} />
                <col style={{ width: '140px' }} />
                <col style={{ width: '120px' }} />
                <col style={{ width: '140px' }} />
                <col style={{ width: '100px' }} />
                <col style={{ width: '130px' }} />
              </colgroup>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Category</th>
                  <th>Confidence</th>
                  <th>Risk</th>
                  <th>Phishing</th>
                  <th>Sentiment</th>
                  <th>Urgency</th>
                  <th>Features</th>
                  <th>Language</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {messages.map((msg) => (
                  <tr key={msg.id} className={`msg-row risk-${msg.risk_level}`}>
                    <td className="cell-time">
                      {new Date(msg.timestamp).toLocaleString('en', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td className="cell-category">
                      <span className={`category-badge badge-${msg.category}`}>
                        {msg.category}
                      </span>
                    </td>
                    <td className="cell-confidence">
                      <div className="confidence-container">
                        <div className="confidence-bar-mini">
                          <div 
                            className="confidence-fill-mini" 
                            style={{ width: `${msg.confidence * 100}%` }}
                          />
                        </div>
                        <span className="confidence-text">{(msg.confidence * 100).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="cell-risk">
                      <span className={`risk-badge risk-${msg.risk_level}`}>
                        {msg.risk_level}
                      </span>
                    </td>
                    <td className="cell-phishing">
                      {msg.is_phishing ? (
                        <span className="phishing-yes">
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 13A6 6 0 118 2a6 6 0 010 12zm1-9H7v5h2V5zm0 6H7v2h2v-2z"/>
                          </svg>
                          Yes
                        </span>
                      ) : (
                        <span className="phishing-no">
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M13.854 3.646a.5.5 0 010 .708l-7 7a.5.5 0 01-.708 0l-3.5-3.5a.5.5 0 11.708-.708L6.5 10.293l6.646-6.647a.5.5 0 01.708 0z"/>
                          </svg>
                          No
                        </span>
                      )}
                    </td>
                    <td className="cell-sentiment">
                      <div className="sentiment-indicator">
                        {msg.sentiment_score > 0.3 ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="sentiment-icon positive">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                            <line x1="9" y1="9" x2="9.01" y2="9"/>
                            <line x1="15" y1="9" x2="15.01" y2="9"/>
                          </svg>
                        ) : msg.sentiment_score < -0.3 ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="sentiment-icon negative">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M16 16s-1.5-2-4-2-4 2-4 2"/>
                            <line x1="9" y1="9" x2="9.01" y2="9"/>
                            <line x1="15" y1="9" x2="15.01" y2="9"/>
                          </svg>
                        ) : (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="sentiment-icon neutral">
                            <circle cx="12" cy="12" r="10"/>
                            <line x1="8" y1="15" x2="16" y2="15"/>
                            <line x1="9" y1="9" x2="9.01" y2="9"/>
                            <line x1="15" y1="9" x2="15.01" y2="9"/>
                          </svg>
                        )}
                        <span className="sentiment-score">
                          {(msg.sentiment_score * 100).toFixed(0)}
                        </span>
                      </div>
                    </td>
                    <td className="cell-urgency">
                      <div className="urgency-indicator">
                        {msg.urgency_score > 0.8 ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="urgency-icon critical">
                            <circle cx="12" cy="12" r="10"/>
                            <line x1="12" y1="8" x2="12" y2="12"/>
                            <line x1="12" y1="16" x2="12.01" y2="16"/>
                          </svg>
                        ) : msg.urgency_score > 0.6 ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="urgency-icon high">
                            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                            <line x1="12" y1="9" x2="12" y2="13"/>
                            <line x1="12" y1="17" x2="12.01" y2="17"/>
                          </svg>
                        ) : msg.urgency_score > 0.4 ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="urgency-icon medium">
                            <circle cx="12" cy="12" r="10"/>
                            <line x1="12" y1="16" x2="12" y2="12"/>
                            <line x1="12" y1="8" x2="12.01" y2="8"/>
                          </svg>
                        ) : (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="urgency-icon low">
                            <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
                            <polyline points="22 4 12 14.01 9 11.01"/>
                          </svg>
                        )}
                        <span className="urgency-score">
                          {(msg.urgency_score * 100).toFixed(0)}
                        </span>
                      </div>
                    </td>
                    <td className="cell-features">
                      <div className="feature-icons-group">
                        {msg.has_urls && (
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="feature-icon" title="Contains URL">
                            <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                            <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                          </svg>
                        )}
                        {msg.has_phone_numbers && (
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="feature-icon" title="Contains Phone">
                            <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>
                          </svg>
                        )}
                        {msg.has_financial_terms && (
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="feature-icon" title="Financial Terms">
                            <line x1="12" y1="1" x2="12" y2="23"/>
                            <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
                          </svg>
                        )}
                        {!msg.has_urls && !msg.has_phone_numbers && !msg.has_financial_terms && (
                          <span className="no-features">—</span>
                        )}
                      </div>
                    </td>
                    <td className="cell-language">
                      <span className="language-badge">{msg.language.toUpperCase()}</span>
                    </td>
                    <td className="cell-actions">
                      <div className="action-buttons">
                        <button 
                          className="action-btn view-btn" 
                          onClick={() => handleViewMessage(msg)}
                          title="View Details"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                          </svg>
                        </button>
                        <button 
                          className="action-btn delete-btn" 
                          onClick={() => handleDeleteMessage(msg.id)}
                          disabled={deletingId === msg.id}
                          title="Delete Message"
                        >
                          {deletingId === msg.id ? (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="spinning">
                              <line x1="12" y1="2" x2="12" y2="6"/>
                              <line x1="12" y1="18" x2="12" y2="22"/>
                              <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
                              <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                              <line x1="2" y1="12" x2="6" y2="12"/>
                              <line x1="18" y1="12" x2="22" y2="12"/>
                              <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
                              <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
                            </svg>
                          ) : (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <polyline points="3 6 5 6 21 6"/>
                              <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                              <line x1="10" y1="11" x2="10" y2="17"/>
                              <line x1="14" y1="11" x2="14" y2="17"/>
                            </svg>
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        <div className="messages-footer">
          <span className="messages-count">
            Showing {messages.length} message{messages.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Model Performance Card */}
      {modelInfo && (
        <div className="chart-card model-performance-card">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">🤖 Active ML Model</div>
              <div className="chart-card-sub">Current model performance metrics</div>
            </div>
          </div>
          <div style={{ marginTop: '1.5rem' }}>
            <div className="model-name-display">
              <span className="model-name-label">Model:</span>
              <span className="model-name-value">{modelInfo.model_name}</span>
            </div>
            <div className="model-metrics-grid">
              <div className="model-metric-box">
                <div className="model-metric-value">{modelInfo.accuracy}%</div>
                <div className="model-metric-label">Test Accuracy</div>
              </div>
              <div className="model-metric-box">
                <div className="model-metric-value">{modelInfo.precision}%</div>
                <div className="model-metric-label">Precision</div>
              </div>
              <div className="model-metric-box">
                <div className="model-metric-value">{modelInfo.recall}%</div>
                <div className="model-metric-label">Recall</div>
              </div>
              <div className="model-metric-box">
                <div className="model-metric-value">{modelInfo.f1_score}%</div>
                <div className="model-metric-label">F1-Score</div>
              </div>
            </div>
            <div className="model-cv-info">
              <span>Cross-Validation: <strong>{modelInfo.cv_mean}%</strong> (±{modelInfo.cv_std}%)</span>
            </div>
            
            {/* Mini Performance Chart */}
            <div className="model-performance-chart">
              <div className="model-performance-chart-title">📊 Performance Breakdown</div>
              <div className="model-performance-bars">
                <div className="model-performance-bar-row">
                  <div className="model-performance-bar-label">Accuracy</div>
                  <div className="model-performance-bar-track">
                    <div 
                      className="model-performance-bar-fill" 
                      style={{ width: `${modelInfo.accuracy}%` }}
                    />
                  </div>
                  <div className="model-performance-bar-value">{modelInfo.accuracy}%</div>
                </div>
                <div className="model-performance-bar-row">
                  <div className="model-performance-bar-label">Precision</div>
                  <div className="model-performance-bar-track">
                    <div 
                      className="model-performance-bar-fill" 
                      style={{ width: `${modelInfo.precision}%` }}
                    />
                  </div>
                  <div className="model-performance-bar-value">{modelInfo.precision}%</div>
                </div>
                <div className="model-performance-bar-row">
                  <div className="model-performance-bar-label">Recall</div>
                  <div className="model-performance-bar-track">
                    <div 
                      className="model-performance-bar-fill" 
                      style={{ width: `${modelInfo.recall}%` }}
                    />
                  </div>
                  <div className="model-performance-bar-value">{modelInfo.recall}%</div>
                </div>
                <div className="model-performance-bar-row">
                  <div className="model-performance-bar-label">F1-Score</div>
                  <div className="model-performance-bar-track">
                    <div 
                      className="model-performance-bar-fill" 
                      style={{ width: `${modelInfo.f1_score}%` }}
                    />
                  </div>
                  <div className="model-performance-bar-value">{modelInfo.f1_score}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Message Detail Modal */}
      {viewingMessage && (
        <div className="modal-overlay" onClick={closeMessageView}>
          <div className="modal-content message-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Message Details</h2>
              <button className="modal-close-btn" onClick={closeMessageView}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            
            <div className="modal-body">
              <div className="detail-section">
                <div className="detail-label">Timestamp</div>
                <div className="detail-value">
                  {new Date(viewingMessage.timestamp).toLocaleString('en', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                  })}
                </div>
              </div>

              <div className="detail-section">
                <div className="detail-label">Message Content</div>
                <div className="detail-value message-content">
                  {viewingMessage.message_text || 'No message text available'}
                </div>
              </div>

              <div className="detail-grid">
                <div className="detail-section">
                  <div className="detail-label">Category</div>
                  <div className="detail-value">
                    <span className={`category-badge badge-${viewingMessage.category}`}>
                      {viewingMessage.category}
                    </span>
                  </div>
                </div>

                <div className="detail-section">
                  <div className="detail-label">Risk Level</div>
                  <div className="detail-value">
                    <span className={`risk-badge risk-${viewingMessage.risk_level}`}>
                      {viewingMessage.risk_level}
                    </span>
                  </div>
                </div>

                <div className="detail-section">
                  <div className="detail-label">Confidence</div>
                  <div className="detail-value">
                    <strong>{(viewingMessage.confidence * 100).toFixed(2)}%</strong>
                  </div>
                </div>

                <div className="detail-section">
                  <div className="detail-label">Phishing</div>
                  <div className="detail-value">
                    {viewingMessage.is_phishing ? (
                      <span className="phishing-yes">Yes</span>
                    ) : (
                      <span className="phishing-no">No</span>
                    )}
                  </div>
                </div>

                <div className="detail-section">
                  <div className="detail-label">Sentiment Score</div>
                  <div className="detail-value">
                    <strong>{(viewingMessage.sentiment_score * 100).toFixed(0)}</strong>
                    <span style={{ marginLeft: '0.5rem', color: 'var(--text-muted)' }}>
                      ({viewingMessage.sentiment_score > 0.3 ? 'Positive' : 
                        viewingMessage.sentiment_score < -0.3 ? 'Negative' : 'Neutral'})
                    </span>
                  </div>
                </div>

                <div className="detail-section">
                  <div className="detail-label">Urgency Score</div>
                  <div className="detail-value">
                    <strong>{(viewingMessage.urgency_score * 100).toFixed(0)}</strong>
                    <span style={{ marginLeft: '0.5rem', color: 'var(--text-muted)' }}>
                      ({viewingMessage.urgency_score > 0.8 ? 'Critical' :
                        viewingMessage.urgency_score > 0.6 ? 'High' :
                        viewingMessage.urgency_score > 0.4 ? 'Medium' : 'Low'})
                    </span>
                  </div>
                </div>

                <div className="detail-section">
                  <div className="detail-label">Language</div>
                  <div className="detail-value">
                    <span className="language-badge">{viewingMessage.language.toUpperCase()}</span>
                  </div>
                </div>

                <div className="detail-section">
                  <div className="detail-label">Message Hash</div>
                  <div className="detail-value" style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                    {viewingMessage.message_hash || 'N/A'}
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <div className="detail-label">Features Detected</div>
                <div className="detail-value">
                  <div className="feature-list">
                    <div className={`feature-item ${viewingMessage.has_urls ? 'active' : 'inactive'}`}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                        <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                      </svg>
                      <span>Contains URLs</span>
                    </div>
                    <div className={`feature-item ${viewingMessage.has_phone_numbers ? 'active' : 'inactive'}`}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>
                      </svg>
                      <span>Contains Phone Numbers</span>
                    </div>
                    <div className={`feature-item ${viewingMessage.has_financial_terms ? 'active' : 'inactive'}`}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="12" y1="1" x2="12" y2="23"/>
                        <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
                      </svg>
                      <span>Contains Financial Terms</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-modal-close" onClick={closeMessageView}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

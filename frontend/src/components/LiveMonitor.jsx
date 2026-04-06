import React, { useState, useRef, useEffect } from 'react';
import { predictSMS } from '../services/api';

function getRiskClass(result) {
  if (!result) return 'risk-low';
  if (result.is_phishing || result.category === 'spam') return 'risk-high';
  if (['high'].includes(result.risk_level)) return 'risk-high';
  if (['medium', 'promotion', 'important'].includes(result.risk_level || result.category)) return 'risk-medium';
  return 'risk-low';
}

function getRiskScore(result) {
  if (!result) return 0;
  if (result.risk_score !== undefined) return Math.round(result.risk_score * 100);
  if (result.is_phishing) return Math.round(70 + result.phishing_score * 30);
  if (result.category === 'spam') return 75;
  if (result.category === 'promotion') return 35;
  return 10;
}

function RiskBadge({ riskClass }) {
  const map = {
    'risk-high':   { label: '🚨 HIGH RISK',   color: '#ef4444', bg: '#fef2f2' },
    'risk-medium': { label: '⚠️ MEDIUM RISK', color: '#f59e0b', bg: '#fffbeb' },
    'risk-low':    { label: '✅ SAFE',         color: '#10b981', bg: '#ecfdf5' },
  };
  const m = map[riskClass] || map['risk-low'];
  return (
    <span style={{
      background: m.bg, color: m.color,
      border: `1px solid ${m.color}`,
      borderRadius: '999px', fontSize: '0.72rem',
      fontWeight: 700, padding: '0.25rem 0.7rem',
    }}>
      {m.label}
    </span>
  );
}

export default function LiveMonitor() {
  const [input, setInput] = useState('');
  const [sender, setSender] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [feed, setFeed] = useState([]);
  const feedRef = useRef(null);

  // Auto-scroll to top when new message arrives
  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = 0;
  }, [feed.length]);

  // Clipboard paste detection
  const handleFocus = async () => {
    if (input.trim()) return;
    try {
      const text = await navigator.clipboard.readText();
      if (text && text.trim().length > 5) setInput(text.trim());
    } catch { /* permission denied — silent */ }
  };

  const handleAnalyze = async () => {
    const msg = input.trim();
    if (!msg || analyzing) return;

    const id = Date.now();
    const from = sender.trim() || 'Unknown Sender';
    const time = new Date();

    // Add to feed immediately as "analyzing"
    setFeed(prev => [{ id, from, text: msg, time, status: 'analyzing', result: null }, ...prev]);
    setAnalyzing(true);
    setInput('');
    setSender('');

    try {
      const result = await predictSMS(msg, 'en');
      setFeed(prev => prev.map(m => m.id === id ? { ...m, status: 'done', result } : m));
    } catch (err) {
      setFeed(prev => prev.map(m => m.id === id ? { ...m, status: 'error' } : m));
    } finally {
      setAnalyzing(false);
    }
  };

  const clearFeed = () => setFeed([]);

  const stats = {
    total: feed.filter(m => m.status === 'done').length,
    threats: feed.filter(m => m.result && (m.result.is_phishing || m.result.category === 'spam')).length,
    safe: feed.filter(m => m.result && !m.result.is_phishing && m.result.category !== 'spam').length,
  };

  return (
    <div className="live-monitor-wrap">

      {/* Header */}
      <div className="lm-header">
        <div className="lm-title-row">
          <div className="lm-icon">📱</div>
          <div>
            <div className="lm-title">Live SMS Monitor</div>
            <div className="lm-subtitle">
              Paste any SMS you receive — it gets analyzed instantly and added to the live feed
            </div>
          </div>
        </div>
        {feed.length > 0 && (
          <button className="lm-btn-stop" onClick={clearFeed}>🗑 Clear Feed</button>
        )}
      </div>

      {/* Stats bar — only shows when there's data */}
      {feed.length > 0 && (
        <div className="lm-stats-bar">
          <div className="lm-stat">
            <span className="lm-stat-num">{stats.total}</span>
            <span className="lm-stat-label">Analyzed</span>
          </div>
          <div className="lm-stat lm-stat-danger">
            <span className="lm-stat-num">{stats.threats}</span>
            <span className="lm-stat-label">Threats</span>
          </div>
          <div className="lm-stat lm-stat-safe">
            <span className="lm-stat-num">{stats.safe}</span>
            <span className="lm-stat-label">Safe</span>
          </div>
          {analyzing && (
            <div className="lm-pulse-wrap">
              <div className="lm-pulse-ring" />
              <div className="lm-pulse-dot" />
              <span className="lm-live-label">ANALYZING</span>
            </div>
          )}
        </div>
      )}

      {/* Input area */}
      <div className="lm-input-area">
        <input
          className="lm-sender-input"
          placeholder="Sender (optional, e.g. VM-HDFC, +91-98...)"
          value={sender}
          onChange={e => setSender(e.target.value)}
        />
        <textarea
          className="lm-msg-input"
          placeholder="Paste the SMS message here... (click to auto-detect from clipboard)"
          value={input}
          onChange={e => setInput(e.target.value)}
          onFocus={handleFocus}
          onKeyDown={e => { if (e.key === 'Enter' && e.ctrlKey) handleAnalyze(); }}
          rows={3}
        />
        <button
          className="lm-btn-analyze"
          onClick={handleAnalyze}
          disabled={!input.trim() || analyzing}
        >
          {analyzing ? (
            <><div className="pulse-dot" /><div className="pulse-dot" /><div className="pulse-dot" /> Analyzing...</>
          ) : (
            '⚡ Analyze Now'
          )}
        </button>
        <div className="lm-input-hint">
          📋 Copy an SMS on your phone → come here → click the box above → it auto-fills · Ctrl+Enter to analyze
        </div>
      </div>

      {/* Empty state */}
      {feed.length === 0 && (
        <div className="lm-empty">
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📨</div>
          <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
            No messages analyzed yet
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '360px', textAlign: 'center' }}>
            Paste any SMS you receive above and click Analyze. Results appear here in real time with risk scores, category, and AI explanation.
          </div>
        </div>
      )}

      {/* Live feed */}
      {feed.length > 0 && (
        <div className="lm-feed" ref={feedRef}>
          {feed.map(msg => {
            const riskClass = getRiskClass(msg.result);
            const score = getRiskScore(msg.result);

            return (
              <div key={msg.id} className={`lm-message ${msg.status === 'analyzing' ? 'lm-analyzing' : riskClass}`}>

                {/* Message header */}
                <div className="lm-msg-header">
                  <div className="lm-sender">
                    <div className="lm-sender-avatar">
                      {msg.from.startsWith('VM-') || msg.from.startsWith('AD-') ? '🏢' : '👤'}
                    </div>
                    <div>
                      <div className="lm-sender-name">{msg.from}</div>
                      <div className="lm-msg-time">
                        {msg.time.toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </div>
                    </div>
                  </div>
                  <div className="lm-msg-status">
                    {msg.status === 'analyzing' && (
                      <div className="lm-analyzing-badge">
                        <div className="pulse-dot" /><div className="pulse-dot" /><div className="pulse-dot" />
                        Analyzing...
                      </div>
                    )}
                    {msg.status === 'done' && <RiskBadge riskClass={riskClass} />}
                    {msg.status === 'error' && (
                      <span style={{ color: '#9ca3af', fontSize: '0.75rem' }}>⚠️ Error</span>
                    )}
                  </div>
                </div>

                {/* Message text */}
                <div className="lm-msg-text">{msg.text}</div>

                {/* Result details */}
                {msg.status === 'done' && msg.result && (
                  <div className="lm-result-row">
                    <div className="lm-result-item">
                      <span className="lm-result-key">Category</span>
                      <span className="lm-result-val">{msg.result.category}</span>
                    </div>
                    <div className="lm-result-item">
                      <span className="lm-result-key">Confidence</span>
                      <span className="lm-result-val">{(msg.result.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="lm-result-item">
                      <span className="lm-result-key">Risk Score</span>
                      <span className="lm-result-val" style={{
                        color: riskClass === 'risk-high' ? '#ef4444' : riskClass === 'risk-medium' ? '#f59e0b' : '#10b981',
                        fontWeight: 700
                      }}>
                        {score}/100
                      </span>
                    </div>
                    <div className="lm-result-item">
                      <span className="lm-result-key">Urgency</span>
                      <span className="lm-result-val">{msg.result.urgency_analysis?.level || 'low'}</span>
                    </div>
                    {msg.result.is_phishing && (
                      <div className="lm-result-item" style={{ width: '100%' }}>
                        <span style={{
                          background: '#fef2f2', color: '#ef4444',
                          border: '1px solid #fecaca', borderRadius: '6px',
                          padding: '0.4rem 0.75rem', fontSize: '0.8rem', fontWeight: 600
                        }}>
                          🎣 Phishing detected — do NOT click any links
                        </span>
                      </div>
                    )}
                    {msg.result.suspicious_keywords?.length > 0 && (
                      <div className="lm-result-item" style={{ width: '100%' }}>
                        <span className="lm-result-key">Flagged words</span>
                        <span className="lm-result-val" style={{ color: '#f59e0b' }}>
                          {msg.result.suspicious_keywords.slice(0, 5).join(', ')}
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {msg.status === 'error' && (
                  <div style={{ fontSize: '0.8rem', color: '#9ca3af', marginTop: '0.5rem' }}>
                    Could not connect to backend. Make sure the server is running.
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <div className="lm-note">
        💡 On mobile: copy an SMS from your messages app → open this page → tap the input box → it auto-fills from clipboard
      </div>
    </div>
  );
}

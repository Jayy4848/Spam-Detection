import React, { useState } from 'react';
import { predictSMS } from '../services/api';
import ResultCard from './ResultCard';

const SAMPLES = {
  spam: "WINNER!! You've been selected for a FREE iPhone 15! Click http://bit.ly/claim-now to claim your prize before it expires. Act NOW!",
  promo: "Exclusive offer for you! Get 50% OFF on all electronics this weekend only. Shop at our store. Valid till Sunday.",
  otp: "Your OTP for login is 847291. Valid for 10 minutes. Do NOT share this code with anyone.",
  important: "Alert: Rs.15,000 debited from your account ending 4821 on 06-Apr. Available balance: Rs.42,300.",
  personal: "Hey! Are you free this evening? Thinking of grabbing dinner at that new place downtown.",
};

const FEATURES = [
  { icon: '🔍', title: 'Spam Detection', desc: 'Identifies spam and promotional messages instantly' },
  { icon: '🎣', title: 'Phishing Guard', desc: 'Detects phishing links and fraud attempts' },
  { icon: '🧠', title: 'Explainable AI', desc: 'Shows exactly why a message was flagged' },
  { icon: '📊', title: 'Risk Scoring', desc: 'Quantified risk score from 0–100' },
  { icon: '🌐', title: 'Multi-language', desc: 'Supports English, Hindi & Marathi' },
  { icon: '⚡', title: 'Real-time', desc: 'Instant analysis in under 100ms' },
];

export default function Home() {
  const [message, setMessage] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await predictSMS(message, language);
      setResult(data);
    } catch (err) {
      setError(err.error || 'Analysis failed. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) handleAnalyze();
  };

  return (
    <main className="home-page">
      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">🛡️ AI-Powered Security</div>
        <h1>
          Protect yourself from<br />
          <span className="gradient-text">SMS fraud & phishing</span>
        </h1>
        <p>
          Paste any SMS message and get an instant AI-powered risk assessment,
          fraud detection, and actionable security advice.
        </p>
        <div className="hero-stats">
          <div className="hero-stat">
            <div className="hero-stat-num">98.9%</div>
            <div className="hero-stat-label">Accuracy</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-num">&lt;100ms</div>
            <div className="hero-stat-label">Response Time</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-num">5</div>
            <div className="hero-stat-label">ML Models</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-num">3</div>
            <div className="hero-stat-label">Languages</div>
          </div>
        </div>
      </section>

      {/* Analyzer */}
      <div className="analyzer-card">
        <div className="analyzer-card-header">
          <h2>Analyze SMS Message</h2>
          <span className="char-count">{message.length} / 1000</span>
        </div>

        <textarea
          className="sms-textarea"
          placeholder="Paste your SMS message here... (Ctrl+Enter to analyze)"
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          maxLength={1000}
        />

        <div className="sample-section">
          <div className="sample-label">Try a sample</div>
          <div className="sample-chips">
            {Object.entries(SAMPLES).map(([type, text]) => (
              <button
                key={type}
                className={`chip chip-${type}`}
                onClick={() => { setMessage(text); setResult(null); setError(''); }}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="lang-section">
          <span className="lang-label">Language:</span>
          <div className="lang-options">
            {[['en', 'English'], ['hi', 'Hindi'], ['mr', 'Marathi']].map(([val, label]) => (
              <button
                key={val}
                className={`lang-btn ${language === val ? 'active' : ''}`}
                onClick={() => setLanguage(val)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <button
          className="btn-analyze"
          onClick={handleAnalyze}
          disabled={loading || !message.trim()}
        >
          {loading ? (
            <>
              <div className="pulse-dot" />
              <div className="pulse-dot" />
              <div className="pulse-dot" />
              Analyzing...
            </>
          ) : (
            <> 🔍 Analyze Message</>
          )}
        </button>

        {error && (
          <div className="error-alert">⚠️ {error}</div>
        )}

        <div className="privacy-bar">
          🔒 Messages are hashed and never stored permanently · Privacy-first design
        </div>
      </div>

      {/* Result */}
      {result && !loading && (
        <div className="result-wrapper">
          <ResultCard result={result} message={message} />
        </div>
      )}

      {/* Features */}
      <div className="features-strip">
        {FEATURES.map((f, i) => (
          <div className="feature-tile" key={i}>
            <div className="feature-tile-icon">{f.icon}</div>
            <div className="feature-tile-title">{f.title}</div>
            <div className="feature-tile-desc">{f.desc}</div>
          </div>
        ))}
      </div>
    </main>
  );
}

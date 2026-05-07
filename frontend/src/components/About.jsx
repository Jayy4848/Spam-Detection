import React, { useState, useEffect } from 'react';
import { getModelInfo } from '../services/api';

const TECH = ['Django REST', 'React 18', 'scikit-learn', 'Naive Bayes', 'TF-IDF', 'Logistic Regression', 'Random Forest', 'Gradient Boosting', 'SVM', 'NLTK', 'Python 3.10', 'SQLite'];

const FEATURES = [
  ['🔍', 'Multi-class SMS classification (Spam, OTP, Promo, Important, Personal)'],
  ['🎣', 'Phishing & fraud detection with URL analysis'],
  ['🧠', 'Explainable AI — word-level importance highlighting'],
  ['📊', 'Risk scoring system (0–100) with actionable advice'],
  ['🌐', 'Multi-language support: English, Hindi, Marathi'],
  ['🔄', 'Adaptive learning from user feedback'],
  ['📈', 'Real-time analytics dashboard'],
  ['⚡', 'Sub-100ms prediction with intelligent caching'],
  ['🏗️', 'Production-grade architecture with monitoring'],
  ['🔒', 'Privacy-first: messages hashed, never stored'],
];

export default function About() {
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    getModelInfo()
      .then(data => setModelInfo(data))
      .catch(err => console.error('Failed to load model info:', err));
  }, []);

  return (
    <div className="about-page">
      <div className="about-hero">
        <div className="hero-badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: '#ede9fe', color: '#6366f1', fontSize: '0.8rem', fontWeight: 600, padding: '0.35rem 0.9rem', borderRadius: '9999px', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.02em' }}>
          Master's Level Project
        </div>
        <h1>TextGuard AI</h1>
        <p>
          An enterprise-grade SMS security assistant built with advanced machine learning,
          explainable AI, and production-ready architecture.
        </p>
      </div>

      {/* Model Performance Card */}
      {modelInfo && (
        <div className="about-card" style={{ marginBottom: '1.25rem', background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)', border: '2px solid rgba(102, 126, 234, 0.2)' }}>
          <h3>🤖 Current Model Performance</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
            <div style={{ textAlign: 'center', padding: '1rem', background: 'white', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--brand-primary)', marginBottom: '0.25rem' }}>{modelInfo.accuracy}%</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Test Accuracy</div>
            </div>
            <div style={{ textAlign: 'center', padding: '1rem', background: 'white', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--brand-primary)', marginBottom: '0.25rem' }}>{modelInfo.precision}%</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Precision</div>
            </div>
            <div style={{ textAlign: 'center', padding: '1rem', background: 'white', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--brand-primary)', marginBottom: '0.25rem' }}>{modelInfo.recall}%</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Recall</div>
            </div>
            <div style={{ textAlign: 'center', padding: '1rem', background: 'white', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--brand-primary)', marginBottom: '0.25rem' }}>{modelInfo.f1_score}%</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>F1-Score</div>
            </div>
          </div>
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(102, 126, 234, 0.1)', borderRadius: 'var(--radius)', textAlign: 'center' }}>
            <div style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>
              <strong style={{ color: 'var(--brand-primary)' }}>Active Model:</strong> {modelInfo.model_name}
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Cross-validation: {modelInfo.cv_mean}% (±{modelInfo.cv_std}%)
            </div>
          </div>
        </div>
      )}

      <div className="about-grid">
        <div className="about-card">
          <h3>🎯 What This Solves</h3>
          <div className="feature-items">
            <div className="feature-item-row"><span>📱</span><span>SMS fraud costs billions annually — users need real-time protection</span></div>
            <div className="feature-item-row"><span>🎣</span><span>Phishing via SMS (smishing) is the fastest-growing attack vector</span></div>
            <div className="feature-item-row"><span>🤷</span><span>Users can't tell legitimate OTPs from fake ones without AI help</span></div>
            <div className="feature-item-row"><span>🌍</span><span>Existing tools don't support Indian languages like Hindi & Marathi</span></div>
          </div>
        </div>

        <div className="about-card">
          <h3>👥 Who This Is For</h3>
          <div className="feature-items">
            <div className="feature-item-row"><span>👴</span><span>Elderly users vulnerable to SMS scams and fraud</span></div>
            <div className="feature-item-row"><span>🏦</span><span>Banking customers receiving financial alerts</span></div>
            <div className="feature-item-row"><span>🛒</span><span>Online shoppers receiving OTPs and delivery updates</span></div>
            <div className="feature-item-row"><span>🏢</span><span>Enterprises monitoring employee SMS communications</span></div>
          </div>
        </div>

        <div className="about-card">
          <h3>🧠 ML Architecture</h3>
          <div className="feature-items">
            <div className="feature-item-row"><span>1️⃣</span><span>Text preprocessing with URL/phone/email tokenization</span></div>
            <div className="feature-item-row"><span>2️⃣</span><span>TF-IDF vectorization with n-gram features (1–3)</span></div>
            <div className="feature-item-row"><span>3️⃣</span><span>5 ML models trained and compared via cross-validation</span></div>
            <div className="feature-item-row"><span>4️⃣</span><span>Best model auto-selected by F1-weighted score</span></div>
            <div className="feature-item-row"><span>5️⃣</span><span>Confidence calibration for reliable probability estimates</span></div>
          </div>
        </div>

        <div className="about-card">
          <h3>⚙️ Tech Stack</h3>
          <div className="tech-tags">
            {TECH.map(t => <span key={t} className="tech-tag">{t}</span>)}
          </div>
        </div>
      </div>

      <div className="about-card" style={{ marginBottom: '1.25rem' }}>
        <h3>✨ Key Features</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.6rem' }}>
          {FEATURES.map(([icon, text], i) => (
            <div key={i} className="feature-item-row">
              <span>{icon}</span><span style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>{text}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="privacy-card">
        <div className="privacy-card-icon">🔒</div>
        <div>
          <h3>Privacy & Security Commitment</h3>
          <p>
            Your messages are never stored in plain text. All content is SHA-256 hashed before logging.
            Only anonymized metadata (category, confidence, timestamp) is retained for analytics.
            This system is designed with privacy-by-default principles and GDPR-ready architecture.
          </p>
        </div>
      </div>
    </div>
  );
}

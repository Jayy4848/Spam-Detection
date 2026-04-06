import React from 'react';

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

import React, { useState } from 'react';
import { submitFeedback } from '../services/api';

const CATEGORY_META = {
  spam:      { icon: '🚨', label: 'Spam Message',       riskClass: 'risk-high' },
  promotion: { icon: '📢', label: 'Promotional',        riskClass: 'risk-medium' },
  otp:       { icon: '🔐', label: 'OTP / Verification', riskClass: 'risk-low' },
  important: { icon: '🏦', label: 'Important Alert',    riskClass: 'risk-medium' },
  personal:  { icon: '💬', label: 'Personal Message',   riskClass: 'risk-low' },
};

const ACTIONS = {
  'risk-high': [
    { icon: '❌', text: 'Do NOT click any links in this message' },
    { icon: '🚫', text: 'Block this sender immediately' },
    { icon: '📵', text: 'Do not call back any numbers provided' },
    { icon: '🛡️', text: 'Report as spam to your carrier' },
  ],
  'risk-medium': [
    { icon: '⚠️', text: 'Verify the sender before taking action' },
    { icon: '🔗', text: 'Avoid clicking links — visit the official site directly' },
    { icon: '📞', text: 'Call the official number if action is required' },
  ],
  'risk-low': [
    { icon: '✅', text: 'This message appears safe' },
    { icon: '🔒', text: 'Never share OTPs or passwords with anyone' },
    { icon: '👁️', text: 'Stay alert for follow-up suspicious messages' },
  ],
};

function getRiskClass(result) {
  if (result.is_phishing || result.category === 'spam') return 'risk-high';
  if (result.risk_level === 'high') return 'risk-high';
  if (result.risk_level === 'medium' || result.category === 'promotion' || result.category === 'important') return 'risk-medium';
  return 'risk-low';
}

function getRiskScore(result) {
  if (result.risk_score !== undefined) return Math.round(result.risk_score * 100);
  if (result.is_phishing) return Math.round(70 + result.phishing_score * 30);
  if (result.category === 'spam') return 75;
  if (result.category === 'promotion') return 35;
  return 10;
}

function buildReasons(result) {
  const reasons = [];
  if (result.is_phishing) reasons.push({ type: 'danger', icon: '🎣', text: 'Phishing attempt detected' });
  if (result.suspicious_keywords?.length > 0)
    reasons.push({ type: 'danger', icon: '🔑', text: `Suspicious keywords: ${result.suspicious_keywords.slice(0, 3).join(', ')}` });
  if (result.suspicious_urls?.length > 0)
    reasons.push({ type: 'danger', icon: '🔗', text: `Suspicious URL detected` });
  if (result.urgency_analysis?.level === 'critical' || result.urgency_analysis?.level === 'high')
    reasons.push({ type: 'warning', icon: '⏰', text: `High urgency language detected` });
  if (result.behavioral_features?.has_financial_terms)
    reasons.push({ type: 'warning', icon: '💰', text: 'Financial terms present' });
  if (result.behavioral_features?.has_phone_numbers)
    reasons.push({ type: 'info', icon: '📞', text: 'Phone number included' });
  if (result.behavioral_features?.has_urls)
    reasons.push({ type: 'info', icon: '🌐', text: 'Contains URL' });
  if (reasons.length === 0)
    reasons.push({ type: 'info', icon: '✅', text: 'No suspicious patterns found' });
  return reasons;
}

export default function ResultCard({ result, message }) {
  const [feedbackDone, setFeedbackDone] = useState(false);
  const [feedbackErr, setFeedbackErr] = useState('');

  const meta = CATEGORY_META[result.category] || CATEGORY_META.personal;
  const riskClass = getRiskClass(result);
  const riskScore = getRiskScore(result);
  const reasons = buildReasons(result);
  const actions = ACTIONS[riskClass];

  const handleFeedback = async (corrected) => {
    try {
      await submitFeedback(result.message_id, result.category, corrected);
      setFeedbackDone(true);
    } catch {
      setFeedbackErr('Could not submit feedback.');
    }
  };

  return (
    <div className="result-card">
      {/* Header — the verdict */}
      <div className={`result-header ${riskClass}`}>
        <div className="verdict-left">
          <div className={`verdict-icon ${riskClass}`}>{meta.icon}</div>
          <div>
            <div className="verdict-title">{meta.label}</div>
            <div className="verdict-subtitle">
              {riskClass === 'risk-high' && '⚠️ High risk — take action immediately'}
              {riskClass === 'risk-medium' && '⚠️ Moderate risk — proceed with caution'}
              {riskClass === 'risk-low' && '✅ Low risk — message appears safe'}
            </div>
          </div>
        </div>
        <div className="verdict-right">
          <div className={`risk-score-circle ${riskClass}`}>
            <span className="risk-score-num">{riskScore}</span>
            <span className="risk-score-label">Risk</span>
          </div>
        </div>
      </div>

      <div className="result-body">
        {/* Why AI flagged this */}
        <div className="reasons-section">
          <div className="section-label">Why AI flagged this</div>
          <div className="reason-pills">
            {reasons.map((r, i) => (
              <span key={i} className={`reason-pill ${r.type}`}>
                {r.icon} {r.text}
              </span>
            ))}
          </div>
        </div>

        {/* Recommended action */}
        <div className={`action-box ${riskClass}`}>
          <div className="action-box-title">
            {riskClass === 'risk-high' ? '🚨 Recommended Actions' :
             riskClass === 'risk-medium' ? '⚠️ Recommended Actions' : '✅ You\'re Safe'}
          </div>
          <div className="action-items">
            {actions.map((a, i) => (
              <div key={i} className="action-item">
                <span>{a.icon}</span>
                <span>{a.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Highlighted text */}
        {result.highlighted_words?.length > 0 && (
          <div className="highlight-section">
            <div className="section-label">Word-level AI explanation</div>
            <div className="highlighted-text">
              {result.highlighted_words.map((item, i) => (
                <span key={i} className={`hl-${item.level}`}>{item.word} </span>
              ))}
            </div>
          </div>
        )}

        {/* Confidence */}
        <div className="confidence-section">
          <div className="confidence-row">
            <span className="confidence-label">Model confidence</span>
            <span className="confidence-pct">{(result.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="conf-bar">
            <div className="conf-fill" style={{ width: `${result.confidence * 100}%` }} />
          </div>
        </div>

        {/* Metrics */}
        <div className="metrics-row">
          <div className="metric-box">
            <div className="metric-box-val">
              {result.sentiment_analysis?.label || 'neutral'}
            </div>
            <div className="metric-box-key">Sentiment</div>
          </div>
          <div className="metric-box">
            <div className="metric-box-val">
              {result.urgency_analysis?.level || 'low'}
            </div>
            <div className="metric-box-key">Urgency</div>
          </div>
          <div className="metric-box">
            <div className="metric-box-val">
              {result.behavioral_features?.word_count || message.split(' ').length}
            </div>
            <div className="metric-box-key">Words</div>
          </div>
        </div>

        {/* Feedback */}
        <div className="feedback-section">
          <div className="feedback-title">Was this classification correct? Help us improve:</div>
          {feedbackDone ? (
            <span className="fb-success">✅ Thanks for your feedback!</span>
          ) : (
            <>
              <div className="feedback-btns">
                {['spam', 'promotion', 'otp', 'important', 'personal'].map(cat => (
                  <button
                    key={cat}
                    className="fb-btn"
                    disabled={result.category === cat}
                    onClick={() => handleFeedback(cat)}
                  >
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </button>
                ))}
              </div>
              {feedbackErr && <div className="error-alert" style={{ marginTop: '0.5rem' }}>{feedbackErr}</div>}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

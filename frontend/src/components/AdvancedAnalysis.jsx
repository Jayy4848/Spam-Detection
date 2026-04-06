import React from 'react';

function AdvancedAnalysis({ result }) {
  if (!result) return null;

  const getSentimentColor = (score) => {
    if (score > 0.3) return '#4caf50';
    if (score < -0.3) return '#f44336';
    return '#ff9800';
  };

  const getUrgencyColor = (score) => {
    if (score > 0.8) return '#d32f2f';
    if (score > 0.6) return '#f57c00';
    if (score > 0.4) return '#fbc02d';
    return '#388e3c';
  };

  const getRiskColor = (level) => {
    const colors = {
      'critical': '#b71c1c',
      'high': '#d32f2f',
      'medium': '#f57c00',
      'low': '#fbc02d',
      'safe': '#388e3c'
    };
    return colors[level] || '#757575';
  };

  return (
    <div className="advanced-analysis-container">
      <h4 className="section-title">🔬 Advanced Analysis</h4>

      {/* Risk Assessment */}
      <div className="analysis-card risk-card">
        <div className="card-header">
          <h5>⚠️ Risk Assessment</h5>
        </div>
        <div className="card-body">
          <div className="risk-indicator">
            <div 
              className="risk-badge" 
              style={{ backgroundColor: getRiskColor(result.risk_level) }}
            >
              {result.risk_level.toUpperCase()}
            </div>
            <div className="risk-score">
              Risk Score: {(result.risk_score * 100).toFixed(1)}%
            </div>
          </div>
          <div className="risk-bar">
            <div 
              className="risk-fill" 
              style={{ 
                width: `${result.risk_score * 100}%`,
                backgroundColor: getRiskColor(result.risk_level)
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Sentiment Analysis */}
      {result.sentiment_analysis && (
        <div className="analysis-card sentiment-card">
          <div className="card-header">
            <h5>😊 Sentiment Analysis</h5>
          </div>
          <div className="card-body">
            <div className="sentiment-display">
              <div className="sentiment-label">{result.sentiment_analysis.label}</div>
              <div 
                className="sentiment-score"
                style={{ color: getSentimentColor(result.sentiment_analysis.score) }}
              >
                Score: {result.sentiment_analysis.score.toFixed(3)}
              </div>
            </div>
            <div className="sentiment-bar">
              <div className="sentiment-negative">Negative</div>
              <div className="sentiment-indicator" style={{ 
                left: `${(result.sentiment_analysis.score + 1) * 50}%`,
                backgroundColor: getSentimentColor(result.sentiment_analysis.score)
              }}></div>
              <div className="sentiment-positive">Positive</div>
            </div>
          </div>
        </div>
      )}

      {/* Urgency Analysis */}
      {result.urgency_analysis && (
        <div className="analysis-card urgency-card">
          <div className="card-header">
            <h5>⏰ Urgency Detection</h5>
          </div>
          <div className="card-body">
            <div className="urgency-display">
              <div className="urgency-level">{result.urgency_analysis.level.toUpperCase()}</div>
              <div 
                className="urgency-score"
                style={{ color: getUrgencyColor(result.urgency_analysis.score) }}
              >
                {(result.urgency_analysis.score * 100).toFixed(1)}%
              </div>
            </div>
            <div className="urgency-bar">
              <div 
                className="urgency-fill"
                style={{ 
                  width: `${result.urgency_analysis.score * 100}%`,
                  backgroundColor: getUrgencyColor(result.urgency_analysis.score)
                }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {/* Behavioral Features */}
      {result.behavioral_features && (
        <div className="analysis-card behavioral-card">
          <div className="card-header">
            <h5>🔍 Behavioral Analysis</h5>
          </div>
          <div className="card-body">
            <div className="feature-grid">
              <div className="feature-item">
                <span className="feature-icon">{result.behavioral_features.has_urls ? '✓' : '✗'}</span>
                <span className="feature-label">URLs Detected</span>
                {result.behavioral_features.url_count > 0 && (
                  <span className="feature-count">({result.behavioral_features.url_count})</span>
                )}
              </div>
              <div className="feature-item">
                <span className="feature-icon">{result.behavioral_features.has_phone_numbers ? '✓' : '✗'}</span>
                <span className="feature-label">Phone Numbers</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">{result.behavioral_features.has_financial_terms ? '✓' : '✗'}</span>
                <span className="feature-label">Financial Terms</span>
                {result.behavioral_features.financial_term_count > 0 && (
                  <span className="feature-count">({result.behavioral_features.financial_term_count})</span>
                )}
              </div>
              <div className="feature-item">
                <span className="feature-icon">📏</span>
                <span className="feature-label">Message Length</span>
                <span className="feature-count">{result.behavioral_features.message_length} chars</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📝</span>
                <span className="feature-label">Word Count</span>
                <span className="feature-count">{result.behavioral_features.word_count} words</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🎯</span>
                <span className="feature-label">Action Requests</span>
                <span className="feature-count">{result.behavioral_features.action_request_count}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Anomaly Detection */}
      {result.anomaly_detection && result.anomaly_detection.is_anomalous && (
        <div className="analysis-card anomaly-card">
          <div className="card-header">
            <h5>🚨 Anomaly Detected</h5>
          </div>
          <div className="card-body">
            <div className="anomaly-score">
              Anomaly Score: {(result.anomaly_detection.anomaly_score * 100).toFixed(1)}%
            </div>
            {result.anomaly_detection.reasons && result.anomaly_detection.reasons.length > 0 && (
              <div className="anomaly-reasons">
                <strong>Reasons:</strong>
                <ul>
                  {result.anomaly_detection.reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Pattern Matches */}
      {result.pattern_matches && result.pattern_matches.length > 0 && (
        <div className="analysis-card pattern-card">
          <div className="card-header">
            <h5>🎯 Threat Pattern Matches</h5>
          </div>
          <div className="card-body">
            <div className="pattern-list">
              {result.pattern_matches.map((match, index) => (
                <div key={index} className="pattern-item">
                  <span className="pattern-text">"{match.pattern}"</span>
                  <span className={`pattern-severity severity-${match.severity}`}>
                    {match.severity}
                  </span>
                  <span className="pattern-frequency">
                    Seen {match.frequency} times
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Temporal Analysis */}
      {result.temporal_analysis && result.temporal_analysis.is_burst && (
        <div className="analysis-card temporal-card">
          <div className="card-header">
            <h5>⚡ Burst Activity Detected</h5>
          </div>
          <div className="card-body">
            <p>Multiple messages detected in short time window - possible spam campaign!</p>
            <div className="temporal-stats">
              <div>Messages in last hour: {result.temporal_analysis.messages_last_hour}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdvancedAnalysis;

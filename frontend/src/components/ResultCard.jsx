import React, { useState } from 'react';
import { submitFeedback } from '../services/api';

function ResultCard({ result, message }) {
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [feedbackError, setFeedbackError] = useState('');

  const handleFeedback = async (correctedCategory) => {
    try {
      await submitFeedback(result.message_id, result.category, correctedCategory);
      setFeedbackSubmitted(true);
      setFeedbackError('');
    } catch (error) {
      setFeedbackError('Failed to submit feedback. Please try again.');
    }
  };

  const getCategoryClass = (category) => {
    return `category-badge category-${category}`;
  };

  const getPhishingAlertClass = () => {
    if (result.phishing_score >= 0.7) return 'phishing-alert high-risk';
    return 'phishing-alert';
  };

  return (
    <div className="result-card">
      <h3 className="text-center mb-3">Analysis Result</h3>

      {/* Category */}
      <div className="text-center">
        <span className={getCategoryClass(result.category)}>
          {result.category.toUpperCase()}
        </span>
      </div>

      {/* Confidence */}
      <div className="mt-3">
        <p><strong>Confidence Score:</strong></p>
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{ width: `${result.confidence * 100}%` }}
          >
            {(result.confidence * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Phishing Alert */}
      {result.is_phishing && (
        <div className={getPhishingAlertClass()}>
          <strong>⚠️ Phishing Alert!</strong>
          <p className="mb-0 mt-1">
            This message shows signs of phishing or fraud (Risk Score: {(result.phishing_score * 100).toFixed(0)}%).
            Be cautious about clicking links or sharing personal information.
          </p>
          {result.suspicious_keywords.length > 0 && (
            <p className="mb-0 mt-2">
              <strong>Suspicious Keywords:</strong> {result.suspicious_keywords.join(', ')}
            </p>
          )}
          {result.suspicious_urls.length > 0 && (
            <p className="mb-0 mt-2">
              <strong>Suspicious URLs:</strong> {result.suspicious_urls.join(', ')}
            </p>
          )}
        </div>
      )}

      {/* Highlighted Text */}
      <div className="mt-3">
        <p><strong>Highlighted Analysis:</strong></p>
        <div className="highlighted-text">
          {result.highlighted_words.map((item, index) => (
            <span key={index} className={`highlight-${item.level}`}>
              {item.word}{' '}
            </span>
          ))}
        </div>
        <small className="text-muted">
          Words are highlighted based on their importance in classification.
          Red = High importance, Yellow = Medium, Normal = Low
        </small>
      </div>

      {/* Model Comparison */}
      <div className="mt-3">
        <p><strong>Model Comparison:</strong></p>
        <div className="model-comparison">
          <div className="model-card">
            <h6>Naive Bayes</h6>
            <p className="mb-1">Category: <strong>{result.model_comparison.naive_bayes.category}</strong></p>
            <p className="mb-0">Confidence: {(result.model_comparison.naive_bayes.confidence * 100).toFixed(1)}%</p>
          </div>
          <div className="model-card">
            <h6>BERT</h6>
            <p className="mb-1">Category: <strong>{result.model_comparison.bert.category}</strong></p>
            <p className="mb-0">
              Confidence: {result.model_comparison.bert.confidence > 0 
                ? `${(result.model_comparison.bert.confidence * 100).toFixed(1)}%`
                : 'Not Available'}
            </p>
          </div>
        </div>
      </div>

      {/* Feedback Section */}
      <div className="feedback-section">
        <p><strong>Was this classification correct?</strong></p>
        {!feedbackSubmitted ? (
          <>
            <p className="text-muted mb-2">Help us improve by providing feedback:</p>
            <div className="feedback-buttons">
              <button
                className="btn-feedback"
                onClick={() => handleFeedback('spam')}
                disabled={result.category === 'spam'}
              >
                Spam
              </button>
              <button
                className="btn-feedback"
                onClick={() => handleFeedback('promotion')}
                disabled={result.category === 'promotion'}
              >
                Promotion
              </button>
              <button
                className="btn-feedback"
                onClick={() => handleFeedback('otp')}
                disabled={result.category === 'otp'}
              >
                OTP
              </button>
              <button
                className="btn-feedback"
                onClick={() => handleFeedback('important')}
                disabled={result.category === 'important'}
              >
                Important
              </button>
              <button
                className="btn-feedback"
                onClick={() => handleFeedback('personal')}
                disabled={result.category === 'personal'}
              >
                Personal
              </button>
            </div>
            {feedbackError && (
              <p className="text-danger mt-2">{feedbackError}</p>
            )}
          </>
        ) : (
          <p className="text-success">✓ Thank you for your feedback!</p>
        )}
      </div>
    </div>
  );
}

export default ResultCard;

import React, { useState } from 'react';
import { predictSMS } from '../services/api';
import ResultCard from './ResultCard';
import AdvancedAnalysis from './AdvancedAnalysis';
import AIFeatures from './AIFeatures';

function Home() {
  const [message, setMessage] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const sampleMessages = {
    spam: "WINNER!! You have won a $1000 prize! Click here to claim now!",
    promotion: "50% off on all items this weekend! Shop now at our store.",
    otp: "Your OTP is 123456. Valid for 10 minutes. Do not share.",
    important: "Your bank account has been debited Rs. 5000. Balance: Rs. 15000.",
    personal: "Hi! How are you? Let's meet for coffee tomorrow."
  };

  const handleAnalyze = async () => {
    if (!message.trim()) {
      setError('Please enter a message to analyze');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await predictSMS(message, language);
      setResult(data);
    } catch (err) {
      setError(err.error || 'Failed to analyze message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (type) => {
    setMessage(sampleMessages[type]);
    setResult(null);
    setError('');
  };

  return (
    <div className="home-container">
      {/* Hero Section */}
      <div className="hero-section">
        <h1>🛡️ Smart SMS Security Assistant</h1>
        <p>AI-powered SMS classification and phishing detection</p>
      </div>

      {/* Input Card */}
      <div className="input-card">
        <h4 className="mb-3">Enter SMS Message</h4>
        
        <textarea
          className="sms-textarea"
          placeholder="Paste your SMS message here..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          maxLength={1000}
        />
        
        <div className="d-flex justify-content-between align-items-center mt-2">
          <small className="text-muted">{message.length}/1000 characters</small>
        </div>

        {/* Language Selector */}
        <div className="language-selector">
          <label>Language:</label>
          <div className="form-check form-check-inline">
            <input
              className="form-check-input"
              type="radio"
              name="language"
              id="lang-en"
              value="en"
              checked={language === 'en'}
              onChange={(e) => setLanguage(e.target.value)}
            />
            <label className="form-check-label" htmlFor="lang-en">
              English
            </label>
          </div>
          <div className="form-check form-check-inline">
            <input
              className="form-check-input"
              type="radio"
              name="language"
              id="lang-hi"
              value="hi"
              checked={language === 'hi'}
              onChange={(e) => setLanguage(e.target.value)}
            />
            <label className="form-check-label" htmlFor="lang-hi">
              Hindi/Hinglish
            </label>
          </div>
          <div className="form-check form-check-inline">
            <input
              className="form-check-input"
              type="radio"
              name="language"
              id="lang-mr"
              value="mr"
              checked={language === 'mr'}
              onChange={(e) => setLanguage(e.target.value)}
            />
            <label className="form-check-label" htmlFor="lang-mr">
              Marathi
            </label>
          </div>
        </div>

        {/* Sample Messages */}
        <div className="mt-3">
          <p className="mb-2"><strong>Try sample messages:</strong></p>
          <div className="d-flex flex-wrap gap-2">
            <button
              className="btn btn-sm btn-outline-primary"
              onClick={() => loadSample('spam')}
            >
              Spam
            </button>
            <button
              className="btn btn-sm btn-outline-warning"
              onClick={() => loadSample('promotion')}
            >
              Promotion
            </button>
            <button
              className="btn btn-sm btn-outline-info"
              onClick={() => loadSample('otp')}
            >
              OTP
            </button>
            <button
              className="btn btn-sm btn-outline-secondary"
              onClick={() => loadSample('important')}
            >
              Important
            </button>
            <button
              className="btn btn-sm btn-outline-success"
              onClick={() => loadSample('personal')}
            >
              Personal
            </button>
          </div>
        </div>

        {/* Analyze Button */}
        <div className="text-center mt-4">
          <button
            className="btn-analyze"
            onClick={handleAnalyze}
            disabled={loading || !message.trim()}
          >
            {loading ? 'Analyzing...' : '🔍 Analyze Message'}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="alert alert-danger mt-3" role="alert">
            {error}
          </div>
        )}
      </div>

      {/* Loading Spinner */}
      {loading && <div className="spinner"></div>}

      {/* Result Card */}
      {result && !loading && (
        <>
          <ResultCard result={result} message={message} />
          {result.ai_features && <AIFeatures aiFeatures={result.ai_features} />}
          <AdvancedAnalysis result={result} />
        </>
      )}

      {/* Privacy Notice */}
      <div className="privacy-notice mt-4">
        <p className="mb-0">
          <strong>🔒 Privacy Notice:</strong> Your messages are analyzed locally and not stored permanently.
          Only anonymized metadata is saved for improving the system.
        </p>
      </div>
    </div>
  );
}

export default Home;

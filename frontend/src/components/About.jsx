import React from 'react';

function About() {
  return (
    <div className="about-container">
      <div className="about-card">
        <h2>🛡️ About Smart SMS Security Assistant</h2>
        <p>
          Smart SMS Security Assistant is an AI-powered web application designed to protect users
          from spam, phishing, and fraudulent SMS messages. Using advanced machine learning and
          natural language processing techniques, it automatically classifies messages and detects
          potential security threats.
        </p>
      </div>

      <div className="about-card">
        <h2>🧠 Core Features</h2>
        <ul className="feature-list">
          <li>
            <strong>Multi-Category Classification:</strong> Automatically categorizes messages into
            Spam, Promotion, OTP, Important, and Personal categories
          </li>
          <li>
            <strong>Dual-Model Approach:</strong> Utilizes both Naive Bayes and BERT models for
            accurate predictions with model comparison
          </li>
          <li>
            <strong>Phishing Detection:</strong> Identifies suspicious keywords, URLs, and patterns
            commonly used in phishing attacks
          </li>
          <li>
            <strong>Explainable AI:</strong> Highlights important words and provides confidence
            scores to explain classification decisions
          </li>
          <li>
            <strong>Multilingual Support:</strong> Supports English, Hinglish, and Marathi text
            analysis
          </li>
          <li>
            <strong>Real-Time Analysis:</strong> Instant classification results with detailed
            risk assessment
          </li>
          <li>
            <strong>User Feedback:</strong> Allows users to correct classifications and help
            improve the model
          </li>
          <li>
            <strong>Analytics Dashboard:</strong> Comprehensive statistics and visualizations
            of analyzed messages
          </li>
        </ul>
      </div>

      <div className="about-card">
        <h2>💻 Technology Stack</h2>
        <div className="row">
          <div className="col-md-6">
            <h5>Frontend</h5>
            <ul>
              <li>React.js 18</li>
              <li>Bootstrap 5</li>
              <li>Chart.js for visualizations</li>
              <li>Axios for API calls</li>
            </ul>
          </div>
          <div className="col-md-6">
            <h5>Backend</h5>
            <ul>
              <li>Django 4.2</li>
              <li>Django REST Framework</li>
              <li>SQLite Database</li>
              <li>CORS Headers</li>
            </ul>
          </div>
        </div>
        <div className="row mt-3">
          <div className="col-md-12">
            <h5>Machine Learning</h5>
            <ul>
              <li>scikit-learn (TF-IDF + Naive Bayes)</li>
              <li>Transformers (BERT/DistilBERT)</li>
              <li>PyTorch</li>
              <li>NLTK for text processing</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="about-card">
        <h2>🔍 How It Works</h2>
        <ol>
          <li>
            <strong>Text Preprocessing:</strong> The input message is cleaned and normalized
            for analysis
          </li>
          <li>
            <strong>Feature Extraction:</strong> TF-IDF vectorization extracts important
            features from the text
          </li>
          <li>
            <strong>Classification:</strong> Both Naive Bayes and BERT models analyze the
            message independently
          </li>
          <li>
            <strong>Phishing Detection:</strong> Suspicious keywords, URLs, and patterns are
            identified
          </li>
          <li>
            <strong>Explanation Generation:</strong> Important words are highlighted and
            confidence scores calculated
          </li>
          <li>
            <strong>Result Presentation:</strong> Comprehensive results with risk assessment
            are displayed
          </li>
        </ol>
      </div>

      <div className="about-card">
        <h2>🎯 Use Cases</h2>
        <ul className="feature-list">
          <li>Personal SMS security screening</li>
          <li>Banking and financial message verification</li>
          <li>OTP and verification code identification</li>
          <li>Promotional message filtering</li>
          <li>Phishing and fraud prevention</li>
          <li>Message organization and prioritization</li>
        </ul>
      </div>

      <div className="about-card">
        <h2>📊 Model Performance</h2>
        <p>
          Our dual-model approach combines the speed of Naive Bayes with the accuracy of BERT:
        </p>
        <ul>
          <li>
            <strong>Naive Bayes:</strong> Fast, lightweight, and efficient for real-time
            classification with good accuracy on common patterns
          </li>
          <li>
            <strong>BERT:</strong> Deep learning model that understands context and nuances
            in language for superior accuracy
          </li>
          <li>
            <strong>Ensemble:</strong> Combining both models provides robust predictions with
            confidence scoring
          </li>
        </ul>
      </div>

      <div className="privacy-notice">
        <h4>🔒 Privacy & Security</h4>
        <p>
          We take your privacy seriously. Your SMS messages are analyzed in real-time and are
          NOT stored permanently. Only anonymized metadata (category, confidence score, timestamp)
          is saved for system improvement and analytics.
        </p>
        <ul className="mb-0">
          <li>No message content is stored in the database</li>
          <li>Only SHA-256 hashes are saved for duplicate detection</li>
          <li>All data is processed locally on the server</li>
          <li>No third-party data sharing</li>
          <li>User feedback is anonymized</li>
        </ul>
      </div>

      <div className="about-card">
        <h2>👨‍💻 Project Information</h2>
        <p>
          This project was developed as a Master's level final year project demonstrating
          practical application of machine learning, natural language processing, and full-stack
          web development skills.
        </p>
        <p>
          <strong>Key Learning Outcomes:</strong>
        </p>
        <ul>
          <li>Implementation of multiple ML models for comparison</li>
          <li>Real-world NLP application development</li>
          <li>Full-stack web application architecture</li>
          <li>RESTful API design and implementation</li>
          <li>Data visualization and analytics</li>
          <li>Security and privacy considerations</li>
        </ul>
      </div>

      <div className="about-card text-center">
        <h3>🚀 Ready to Secure Your Messages?</h3>
        <p>Start analyzing your SMS messages now!</p>
        <a href="/" className="btn btn-primary btn-lg">
          Go to Home
        </a>
      </div>
    </div>
  );
}

export default About;

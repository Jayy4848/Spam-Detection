import React, { useState } from 'react';

function AIFeatures({ aiFeatures }) {
  const [expandedSection, setExpandedSection] = useState(null);

  if (!aiFeatures) return null;

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="ai-features-container">
      <h3 className="ai-title">🤖 AI/ML Analysis</h3>
      <p className="ai-subtitle">Advanced Machine Learning & Deep Learning Features</p>

      {/* Neural Network Features */}
      <div className="ai-card">
        <div 
          className="ai-card-header" 
          onClick={() => toggleSection('neural')}
        >
          <h4>🧠 Neural Network Analysis</h4>
          <span className="toggle-icon">{expandedSection === 'neural' ? '▼' : '▶'}</span>
        </div>
        {expandedSection === 'neural' && (
          <div className="ai-card-body">
            <div className="ai-metrics-grid">
              <div className="ai-metric">
                <div className="metric-label">Character Diversity</div>
                <div className="metric-value">
                  {(aiFeatures.neural_features.char_diversity * 100).toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill neural-fill"
                    style={{ width: `${aiFeatures.neural_features.char_diversity * 100}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="ai-metric">
                <div className="metric-label">Word Diversity</div>
                <div className="metric-value">
                  {(aiFeatures.neural_features.word_diversity * 100).toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill neural-fill"
                    style={{ width: `${aiFeatures.neural_features.word_diversity * 100}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="ai-metric">
                <div className="metric-label">Sequence Coherence</div>
                <div className="metric-value">
                  {(aiFeatures.neural_features.sequence_coherence * 100).toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill neural-fill"
                    style={{ width: `${aiFeatures.neural_features.sequence_coherence * 100}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="ai-metric">
                <div className="metric-label">Neural Attention Score</div>
                <div className="metric-value">
                  {(aiFeatures.neural_features.attention_score * 100).toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill neural-fill"
                    style={{ width: `${aiFeatures.neural_features.attention_score * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
            
            <div className="neural-summary">
              <strong>Combined Neural Score:</strong> 
              <span className="neural-score">
                {(aiFeatures.neural_features.combined_score * 100).toFixed(1)}%
              </span>
            </div>
            
            {aiFeatures.neural_features.important_words && aiFeatures.neural_features.important_words.length > 0 && (
              <div className="important-words">
                <strong>Neural Network Identified Keywords:</strong>
                <div className="word-tags">
                  {aiFeatures.neural_features.important_words.map((word, index) => (
                    <span key={index} className="word-tag neural-tag">{word}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Transfer Learning */}
      <div className="ai-card">
        <div 
          className="ai-card-header" 
          onClick={() => toggleSection('transfer')}
        >
          <h4>🔄 Transfer Learning</h4>
          <span className="toggle-icon">{expandedSection === 'transfer' ? '▼' : '▶'}</span>
        </div>
        {expandedSection === 'transfer' && (
          <div className="ai-card-body">
            <div className="transfer-status">
              <div className={`transfer-badge ${aiFeatures.transfer_learning.benefit ? 'active' : 'inactive'}`}>
                {aiFeatures.transfer_learning.benefit ? '✓ Transfer Learning Applied' : '○ No Transfer Benefit'}
              </div>
              {aiFeatures.transfer_learning.benefit && (
                <div className="confidence-boost">
                  Confidence Boost: +{(aiFeatures.transfer_learning.confidence_boost * 100).toFixed(1)}%
                </div>
              )}
            </div>
            
            <div className="knowledge-alignment">
              <h5>Pre-trained Knowledge Alignment:</h5>
              <div className="alignment-grid">
                {Object.entries(aiFeatures.transfer_learning.alignments).map(([type, score]) => (
                  <div key={type} className="alignment-item">
                    <div className="alignment-label">{type.replace('_', ' ')}</div>
                    <div className="alignment-bar">
                      <div 
                        className="alignment-fill"
                        style={{ 
                          width: `${score * 100}%`,
                          backgroundColor: score > 0.5 ? '#4caf50' : score > 0.3 ? '#ff9800' : '#9e9e9e'
                        }}
                      ></div>
                    </div>
                    <div className="alignment-score">{(score * 100).toFixed(0)}%</div>
                  </div>
                ))}
              </div>
              
              <div className="dominant-knowledge">
                <strong>Dominant Knowledge Base:</strong> 
                <span className="knowledge-type">{aiFeatures.transfer_learning.dominant_knowledge.replace('_', ' ')}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Attention Mechanism */}
      <div className="ai-card">
        <div 
          className="ai-card-header" 
          onClick={() => toggleSection('attention')}
        >
          <h4>👁️ Multi-Head Attention Mechanism</h4>
          <span className="toggle-icon">{expandedSection === 'attention' ? '▼' : '▶'}</span>
        </div>
        {expandedSection === 'attention' && (
          <div className="ai-card-body">
            <p className="attention-description">
              Advanced attention mechanism analyzing text from multiple perspectives
            </p>
            
            <div className="attention-heads">
              {aiFeatures.attention_mechanism.multi_head_attention.map((head, index) => (
                <div key={index} className="attention-head">
                  <div className="head-title">
                    <span className="head-icon">
                      {head.query_type === 'threat' ? '⚠️' : 
                       head.query_type === 'sentiment' ? '😊' : '⏰'}
                    </span>
                    <span className="head-name">{head.query_type} Attention</span>
                    <span className="head-score">{(head.top_score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="head-words">
                    {head.focused_words.map((word, idx) => (
                      <span key={idx} className={`attention-word ${head.query_type}-attention`}>
                        {word}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="combined-attention">
              <strong>Combined Attention Focus:</strong>
              <div className="focus-words">
                {aiFeatures.attention_mechanism.combined_focus.map((word, index) => (
                  <span key={index} className="focus-word">{word}</span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Ensemble Learning */}
      <div className="ai-card">
        <div 
          className="ai-card-header" 
          onClick={() => toggleSection('ensemble')}
        >
          <h4>🎯 Ensemble Learning</h4>
          <span className="toggle-icon">{expandedSection === 'ensemble' ? '▼' : '▶'}</span>
        </div>
        {expandedSection === 'ensemble' && (
          <div className="ai-card-body">
            <div className="ensemble-result">
              <div className="ensemble-prediction">
                <div className="prediction-label">Ensemble Prediction:</div>
                <div className="prediction-value">{aiFeatures.ensemble_prediction.final_prediction.toUpperCase()}</div>
              </div>
              <div className="ensemble-confidence">
                <div className="confidence-label">Ensemble Confidence:</div>
                <div className="confidence-value">
                  {(aiFeatures.ensemble_prediction.ensemble_confidence * 100).toFixed(1)}%
                </div>
              </div>
            </div>
            <p className="ensemble-description">
              Multiple ML models combined using weighted voting for robust predictions
            </p>
          </div>
        )}
      </div>

      {/* Confidence Calibration */}
      <div className="ai-card">
        <div 
          className="ai-card-header" 
          onClick={() => toggleSection('calibration')}
        >
          <h4>📊 Confidence Calibration</h4>
          <span className="toggle-icon">{expandedSection === 'calibration' ? '▼' : '▶'}</span>
        </div>
        {expandedSection === 'calibration' && (
          <div className="ai-card-body">
            <div className="calibration-comparison">
              <div className="calibration-item">
                <div className="calib-label">Original Confidence</div>
                <div className="calib-value original">
                  {(aiFeatures.confidence_calibration.original * 100).toFixed(2)}%
                </div>
              </div>
              <div className="calibration-arrow">→</div>
              <div className="calibration-item">
                <div className="calib-label">Calibrated Confidence</div>
                <div className="calib-value calibrated">
                  {(aiFeatures.confidence_calibration.calibrated * 100).toFixed(2)}%
                </div>
              </div>
            </div>
            
            <div className="calibration-adjustment">
              <strong>Adjustment:</strong> 
              <span className={`adjustment-value ${aiFeatures.confidence_calibration.adjustment >= 0 ? 'positive' : 'negative'}`}>
                {aiFeatures.confidence_calibration.adjustment >= 0 ? '+' : ''}
                {(aiFeatures.confidence_calibration.adjustment * 100).toFixed(2)}%
              </span>
            </div>
            
            <p className="calibration-description">
              Confidence scores calibrated based on historical accuracy to provide more reliable predictions
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default AIFeatures;

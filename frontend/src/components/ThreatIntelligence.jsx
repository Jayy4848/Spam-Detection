import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ThreatIntelligence() {
  const [threatData, setThreatData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchThreatData();
  }, []);

  const fetchThreatData = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/threat-intelligence/`);
      setThreatData(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load threat intelligence data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="spinner"></div>;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!threatData) return null;

  return (
    <div className="threat-intelligence-container">
      <h2 className="page-title">🛡️ Threat Intelligence</h2>

      {/* Summary Cards */}
      <div className="threat-summary">
        <div className="threat-card">
          <div className="threat-number">{threatData.total_active_patterns}</div>
          <div className="threat-label">Active Threat Patterns</div>
        </div>
        <div className="threat-card high-risk">
          <div className="threat-number">{threatData.high_risk_count_24h}</div>
          <div className="threat-label">High Risk (24h)</div>
        </div>
      </div>

      {/* Threat Trend Chart */}
      <div className="chart-container">
        <h4>Phishing Trend (7 Days)</h4>
        <div className="trend-chart">
          {threatData.threat_trend_7days.map((item, index) => (
            <div key={index} className="trend-bar-container">
              <div 
                className="trend-bar" 
                style={{ height: `${Math.max(item.count * 20, 5)}px` }}
              >
                <span className="trend-count">{item.count}</span>
              </div>
              <div className="trend-date">{new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Threat Patterns Table */}
      <div className="patterns-container">
        <h4>Recent Threat Patterns</h4>
        <div className="patterns-table">
          <table className="table">
            <thead>
              <tr>
                <th>Pattern</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Frequency</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {threatData.threat_patterns.map((pattern, index) => (
                <tr key={index}>
                  <td className="pattern-text">"{pattern.pattern}"</td>
                  <td>{pattern.type}</td>
                  <td>
                    <span className={`severity-badge severity-${pattern.severity}`}>
                      {pattern.severity}
                    </span>
                  </td>
                  <td>{pattern.frequency}</td>
                  <td>{new Date(pattern.last_seen).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <button className="btn btn-primary mt-3" onClick={fetchThreatData}>
        🔄 Refresh Data
      </button>
    </div>
  );
}

export default ThreatIntelligence;

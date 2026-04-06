import React, { useState, useEffect } from 'react';
import { getStats } from '../services/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
      setError('');
    } catch (err) {
      setError('Failed to load statistics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="alert alert-danger">{error}</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="dashboard-container">
        <div className="alert alert-info">No data available yet. Start analyzing messages!</div>
      </div>
    );
  }

  // Category Distribution Chart
  const categoryData = {
    labels: stats.category_distribution.map(item => item.category.toUpperCase()),
    datasets: [
      {
        label: 'Messages by Category',
        data: stats.category_distribution.map(item => item.count),
        backgroundColor: [
          'rgba(231, 76, 60, 0.7)',
          'rgba(243, 156, 18, 0.7)',
          'rgba(33, 150, 243, 0.7)',
          'rgba(156, 39, 176, 0.7)',
          'rgba(80, 200, 120, 0.7)',
        ],
        borderColor: [
          'rgba(231, 76, 60, 1)',
          'rgba(243, 156, 18, 1)',
          'rgba(33, 150, 243, 1)',
          'rgba(156, 39, 176, 1)',
          'rgba(80, 200, 120, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  // Daily Trends Chart
  const trendsData = {
    labels: stats.daily_trends.map(item => {
      const date = new Date(item.date);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    }),
    datasets: [
      {
        label: 'Messages Analyzed',
        data: stats.daily_trends.map(item => item.count),
        borderColor: 'rgba(74, 144, 226, 1)',
        backgroundColor: 'rgba(74, 144, 226, 0.2)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  // Spam vs Ham Pie Chart
  const spamHamData = {
    labels: ['Spam', 'Ham (Not Spam)'],
    datasets: [
      {
        data: [stats.spam_count, stats.ham_count],
        backgroundColor: [
          'rgba(231, 76, 60, 0.7)',
          'rgba(80, 200, 120, 0.7)',
        ],
        borderColor: [
          'rgba(231, 76, 60, 1)',
          'rgba(80, 200, 120, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  return (
    <div className="dashboard-container">
      <h2 className="text-center mb-4">📊 Analytics Dashboard</h2>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{stats.total_messages}</div>
          <div className="stat-label">Total Messages Analyzed</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#e74c3c' }}>
            {stats.spam_count}
          </div>
          <div className="stat-label">Spam Messages</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#50c878' }}>
            {stats.ham_count}
          </div>
          <div className="stat-label">Ham Messages</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#f39c12' }}>
            {stats.phishing_count}
          </div>
          <div className="stat-label">Phishing Detected</div>
        </div>
      </div>

      {/* Spam Ratio */}
      <div className="chart-container">
        <h4 className="chart-title">Spam Detection Rate</h4>
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{
              width: `${stats.spam_ratio}%`,
              background: stats.spam_ratio > 50
                ? 'linear-gradient(90deg, #e74c3c, #c0392b)'
                : 'linear-gradient(90deg, #50c878, #45b068)',
            }}
          >
            {stats.spam_ratio.toFixed(1)}% Spam
          </div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="row">
        <div className="col-md-6 mb-4">
          <div className="chart-container">
            <h4 className="chart-title">Category Distribution</h4>
            <Bar
              data={categoryData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      stepSize: 1,
                    },
                  },
                },
              }}
            />
          </div>
        </div>
        <div className="col-md-6 mb-4">
          <div className="chart-container">
            <h4 className="chart-title">Spam vs Ham</h4>
            <Pie
              data={spamHamData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'bottom',
                  },
                },
              }}
            />
          </div>
        </div>
      </div>

      {/* Daily Trends */}
      <div className="chart-container">
        <h4 className="chart-title">7-Day Trend</h4>
        <Line
          data={trendsData}
          options={{
            responsive: true,
            plugins: {
              legend: {
                display: false,
              },
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  stepSize: 1,
                },
              },
            },
          }}
        />
      </div>

      {/* Average Confidence */}
      {Object.keys(stats.average_confidence).length > 0 && (
        <div className="chart-container">
          <h4 className="chart-title">Average Confidence by Category</h4>
          <div className="model-comparison">
            {Object.entries(stats.average_confidence).map(([category, confidence]) => (
              <div key={category} className="model-card">
                <h6>{category.toUpperCase()}</h6>
                <div className="stat-number" style={{ fontSize: '1.5rem' }}>
                  {(confidence * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Additional Stats */}
      <div className="chart-container">
        <h4 className="chart-title">Additional Statistics</h4>
        <div className="row">
          <div className="col-md-4">
            <p><strong>User Feedback Received:</strong></p>
            <p className="stat-number" style={{ fontSize: '2rem' }}>
              {stats.feedback_count}
            </p>
          </div>
          <div className="col-md-4">
            <p><strong>Language Distribution:</strong></p>
            {stats.language_distribution.map(item => (
              <p key={item.language}>
                {item.language.toUpperCase()}: {item.count}
              </p>
            ))}
          </div>
          <div className="col-md-4">
            <p><strong>System Status:</strong></p>
            <p className="text-success">✓ All systems operational</p>
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="text-center mt-4">
        <button className="btn btn-primary" onClick={fetchStats}>
          🔄 Refresh Statistics
        </button>
      </div>
    </div>
  );
}

export default Dashboard;

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const predictSMS = async (message, language = 'en') => {
  try {
    const response = await api.post('/predict/', { message, language });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to analyze message' };
  }
};

export const submitFeedback = async (messageId, originalCategory, correctedCategory) => {
  try {
    const response = await api.post('/feedback/', {
      message_id: messageId,
      original_category: originalCategory,
      corrected_category: correctedCategory,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to submit feedback' };
  }
};

export const getStats = async () => {
  try {
    const response = await api.get('/stats/');
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to fetch statistics' };
  }
};

export const checkHealth = async () => {
  try {
    const response = await api.get('/health/');
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'API is not responding' };
  }
};

export default api;

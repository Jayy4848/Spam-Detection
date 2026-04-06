import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Warn if using HTTP in production
if (process.env.NODE_ENV === 'production' && API_URL.startsWith('http://')) {
  console.warn('[Security] API URL is using HTTP in production. Use HTTPS.');
}

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000, // 15 second timeout — prevents hanging requests
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest', // Helps identify AJAX requests
  },
  withCredentials: false, // Don't send cookies cross-origin
});

// ── Request interceptor ──────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    // Add a unique request ID for tracing
    config.headers['X-Request-ID'] = crypto.randomUUID
      ? crypto.randomUUID()
      : Math.random().toString(36).slice(2);

    // Strip any accidentally included sensitive fields
    if (config.data && typeof config.data === 'object') {
      const safe = { ...config.data };
      delete safe.password;
      delete safe.token;
      delete safe.secret;
      config.data = safe;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor ─────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Never expose raw error details to the UI
    if (error.response) {
      const status = error.response.status;

      if (status === 429) {
        return Promise.reject({ error: 'Too many requests. Please wait a moment and try again.' });
      }
      if (status === 400) {
        return Promise.reject({ error: error.response.data?.error || 'Invalid request.' });
      }
      if (status >= 500) {
        return Promise.reject({ error: 'Server error. Please try again later.' });
      }

      return Promise.reject(error.response.data || { error: 'Request failed.' });
    }

    if (error.code === 'ECONNABORTED') {
      return Promise.reject({ error: 'Request timed out. Check your connection.' });
    }

    return Promise.reject({ error: 'Cannot reach server. Is the backend running?' });
  }
);

// ── Input validation before sending ─────────────────────────────────────────
function validateMessage(message) {
  if (!message || typeof message !== 'string') throw new Error('Message must be a string');
  const trimmed = message.trim();
  if (trimmed.length === 0) throw new Error('Message cannot be empty');
  if (trimmed.length > 1000) throw new Error('Message too long (max 1000 characters)');
  return trimmed;
}

// ── API methods ──────────────────────────────────────────────────────────────
export const predictSMS = async (message, language = 'en') => {
  const safeMessage  = validateMessage(message);
  const safeLanguage = ['en', 'hi', 'mr'].includes(language) ? language : 'en';

  const response = await api.post('/predict/', {
    message: safeMessage,
    language: safeLanguage,
  });
  return response.data;
};

export const submitFeedback = async (messageId, originalCategory, correctedCategory) => {
  const validCategories = ['spam', 'promotion', 'otp', 'important', 'personal'];

  if (!validCategories.includes(originalCategory))  throw new Error('Invalid original category');
  if (!validCategories.includes(correctedCategory)) throw new Error('Invalid corrected category');
  if (originalCategory === correctedCategory)       throw new Error('Categories must differ');

  const response = await api.post('/feedback/', {
    message_id:         String(messageId),
    original_category:  originalCategory,
    corrected_category: correctedCategory,
  });
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/stats/');
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/health/');
  return response.data;
};

export default api;

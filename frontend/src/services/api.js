import axios from 'axios';

// Determine the backend URL based on the environment
const getBaseUrl = () => {
  // For development environment
  if (process.env.NODE_ENV === 'development') {
    // Try to use the environment variable if set, otherwise default to localhost:5000
    const devUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    console.log('🔧 API using development URL:', devUrl);
    return devUrl;
  }
  // For production, use relative URL (same domain as frontend)
  console.log('🔧 API using production URL: relative path');
  return '';
};

const baseURL = getBaseUrl();

console.log('🔌 API connecting to backend at:', baseURL);

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes timeout for scraping operations
});

export default api;

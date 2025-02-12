import axios from 'axios';
import { toast } from 'react-toastify';

// Create an Axios instance
const axiosInstance = axios.create({
  baseURL: 'http://localhost:5000/api',  // Replace with your backend's base URL
  headers: {
    'Content-Type': 'application/json'
  }
});

// Optional: Add interceptors for handling responses globally
axiosInstance.interceptors.response.use(
  response => response,
  error => {
    const errorMsg = error.response?.data?.error || 'An unexpected error occurred.';
    toast.error(errorMsg);
    return Promise.reject(error);
  }
);

export default axiosInstance;

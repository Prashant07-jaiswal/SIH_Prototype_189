import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercept requests to add token
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  return api.post('/api/auth/token', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
};

export const getGraphData = () => api.get('/api/graph/current');
export const getGraphStats = () => api.get('/api/graph/stats');
export const getKeyPlayers = () => api.get('/api/analytics/key-players');
export const getCommunities = () => api.get('/api/analytics/communities');
export const runIngestion = () => api.post('/api/ingest/all');
export const queryNetwork = (query) => api.post('/api/query', { query });

export default api;

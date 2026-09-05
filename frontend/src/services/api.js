import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getGraphData = () => api.get('/api/graph/current');
export const getGraphStats = () => api.get('/api/graph/stats');
export const getKeyPlayers = () => api.get('/api/analytics/key-players');
export const getCommunities = () => api.get('/api/analytics/communities');
export const runIngestion = () => api.post('/api/ingest/all');

export default api;

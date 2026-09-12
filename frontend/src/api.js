import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const signup = async (email, username, password) => {
  const response = await api.post('/signup', { email, username, password });
  return response.data;
};

export const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await api.post('/token', formData);
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/users/me');
  return response.data;
};

// WytPass OAuth Configuration
const WYTPASS_CLIENT_ID = 'wp_e48c48109ebebe4ea9d0';
const WYTPASS_AUTHORIZE_URL = 'https://wytnet.com/oauth/authorize';

export const initiateWytPassLogin = () => {
  // Generate PKCE verifier
  const verifier = crypto.randomUUID() + crypto.randomUUID();
  localStorage.setItem('pkce_verifier', verifier);
  
  // Create code challenge
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  crypto.subtle.digest('SHA-256', data).then(hash => {
    const challenge = btoa(String.fromCharCode(...new Uint8Array(hash)))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
    
    // Redirect to WytPass
    const redirectUri = `${window.location.origin}/auth/callback`;
    const params = new URLSearchParams({
      client_id: WYTPASS_CLIENT_ID,
      redirect_uri: redirectUri,
      response_type: 'code',
      scope: 'openid email profile',
      code_challenge: challenge,
      code_challenge_method: 'S256'
    });
    
    window.location.href = `${WYTPASS_AUTHORIZE_URL}?${params.toString()}`;
  });
};

export const exchangeWytPassCode = async (code) => {
  const verifier = localStorage.getItem('pkce_verifier');
  if (!verifier) {
    throw new Error('PKCE verifier not found');
  }
  
  const response = await api.post('/auth/wytpass/token', {
    code,
    code_verifier: verifier
  });
  
  localStorage.removeItem('pkce_verifier');
  return response.data;
};

export const calculateBMI = async (weight, height) => {
  const response = await api.post('/calculate/bmi', { weight, height });
  return response.data;
};

export const calculateAge = async (birth_date) => {
  const response = await api.post('/calculate/age', { birth_date });
  return response.data;
};

export const calculateGST = async (amount, gst_rate) => {
  const response = await api.post('/calculate/gst', { amount, gst_rate });
  return response.data;
};

export const calculateEBBill = async (units, rate_per_unit) => {
  const response = await api.post('/calculate/eb-bill', { units, rate_per_unit });
  return response.data;
};

export default api;

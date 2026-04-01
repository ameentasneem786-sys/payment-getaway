import axios from "axios";

const API_BASE_URL = location.host === 'localhost' ?
  "http://127.0.0.1:5000" : 'https://payment-getaway-0oi0.onrender.com'

const API = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default API;

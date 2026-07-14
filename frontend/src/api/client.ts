import axios from "axios";

// API base URL is environment-configured (CORS env base URL, task 1.3).
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

const client = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

export default client;

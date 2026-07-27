import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

const client = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const path = window.location.pathname;
      if (path.startsWith("/admin") && !path.startsWith("/admin/login")) {
        window.location.href = "/admin/login";
      } else if (path.startsWith("/employee") && !path.startsWith("/employee/redeem")) {
        window.location.href = "/employee/redeem";
      }
    }
    return Promise.reject(error);
  }
);

export default client;

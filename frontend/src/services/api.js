import axios from "axios";

const instance = axios.create({
  baseURL: "http://127.0.0.1:5000/api", // Flask backend URL
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ Automatically attach Authorization header with token
instance.interceptors.request.use(
  (config) => {
    const storedUser = localStorage.getItem("research_user");
    if (storedUser) {
      try {
        const { token } = JSON.parse(storedUser);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (err) {
        console.error("Error parsing stored user:", err);
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default instance;

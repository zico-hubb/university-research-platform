import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "../services/api";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage on app start
  useEffect(() => {
    const stored = localStorage.getItem("research_user");
    if (stored) {
      const parsed = JSON.parse(stored);

      // Check token expiration (optional: decode JWT to verify exp)
      setUser(parsed);
    }
    setLoading(false);
  }, []);

  // Login function
  const login = async (email, password) => {
    try {
      const res = await axios.post("/auth/login", { email, password });
      const userData = res.data.user || {};
      const token = res.data.token; // ✅ matches backend

      const combined = { ...userData, token };
      setUser(combined);
      localStorage.setItem("research_user", JSON.stringify(combined));

      navigate("/dashboard");
    } catch (err) {
      throw err.response?.data?.error || "Login failed";
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    localStorage.removeItem("research_user");
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {!loading && children} {/* Wait until user load is complete */}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

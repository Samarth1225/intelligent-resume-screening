import { createContext, useContext, useState, useCallback } from "react";
import { authApi, apiErrorMessage } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => localStorage.getItem("irscs_user"));

  const login = useCallback(async (email, password) => {
    try {
      const data = await authApi.login(email, password);
      localStorage.setItem("irscs_token", data.access_token);
      localStorage.setItem("irscs_user", data.user_email);
      setUser(data.user_email);
      return { ok: true };
    } catch (err) {
      return { ok: false, error: apiErrorMessage(err, "Invalid email or password.") };
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("irscs_token");
    localStorage.removeItem("irscs_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { authApi } from "../api/endpoints";

interface AdminUser {
  username: string;
}

interface EmployeeUser {
  id: number;
  name: string;
}

interface AuthContextType {
  admin: AdminUser | null;
  employee: EmployeeUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  redeem: (token: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [admin, setAdmin] = useState<AdminUser | null>(null);
  const [employee, setEmployee] = useState<EmployeeUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authApi
      .status()
      .then((r) => {
        if (r.data.admin) setAdmin(r.data.admin);
        if (r.data.employee) setEmployee(r.data.employee);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const login = async (username: string, password: string) => {
    const r = await authApi.login({ username, password });
    setAdmin(r.data.user);
  };

  const logout = async () => {
    await authApi.logout();
    setAdmin(null);
  };

  const redeem = async (token: string) => {
    const r = await authApi.redeem({ token });
    setEmployee(r.data.employee);
  };

  return (
    <AuthContext.Provider value={{ admin, employee, loading, login, logout, redeem }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

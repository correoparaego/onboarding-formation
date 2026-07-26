import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

interface Props {
  children: React.ReactNode;
  role: "admin" | "employee";
}

export default function ProtectedRoute({ children, role }: Props) {
  const { admin, employee, loading } = useAuth();

  if (loading) return <p style={{ color: "var(--color-text-muted)", padding: "var(--space-lg)", textAlign: "center" }}>Cargando...</p>;

  if (role === "admin" && !admin) {
    return <Navigate to="/admin/login" replace />;
  }

  if (role === "employee" && !employee) {
    return <Navigate to="/employee/redeem" replace />;
  }

  return <>{children}</>;
}

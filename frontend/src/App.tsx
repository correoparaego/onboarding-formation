import { Routes, Route, Link } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import AdminApp from "./admin/AdminApp";
import EmployeeApp from "./employee/EmployeeApp";
import AdminLogin from "./auth/AdminLogin";
import EmployeeRedeem from "./auth/EmployeeRedeem";
import { ThemeToggle } from "./components/ui";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin/*" element={<AdminApp />} />
        <Route path="/employee/redeem" element={<EmployeeRedeem />} />
        <Route path="/employee/*" element={<EmployeeApp />} />
        <Route
          path="*"
          element={
            <div data-testid="landing-page" style={{ padding: "var(--space-lg)", maxWidth: 600, margin: "0 auto" }}>
              <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "var(--space-md)" }}>
                <ThemeToggle />
              </div>
              <h1 style={{ fontSize: "var(--font-size-3xl)", marginBottom: "var(--space-lg)" }}>Formación Inicial</h1>
              <nav role="navigation">
                <ul style={{ listStyle: "none", padding: 0, display: "flex", gap: "var(--space-md)" }}>
                  <li>
                    <Link data-testid="admin-access-link" to="/admin" style={{ padding: "var(--space-sm) var(--space-md)", border: "1px solid var(--color-border)", borderRadius: "var(--radius-sm)" }}>Acceso administración</Link>
                  </li>
                  <li>
                    <Link data-testid="employee-access-link" to="/employee" style={{ padding: "var(--space-sm) var(--space-md)", border: "1px solid var(--color-border)", borderRadius: "var(--radius-sm)" }}>Acceso empleado</Link>
                  </li>
                </ul>
              </nav>
            </div>
          }
        />
      </Routes>
    </AuthProvider>
  );
}

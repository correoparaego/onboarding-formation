import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { Button, Input, Card, ThemeToggle } from "../components/ui";
import { useToast } from "../contexts/ToastContext";

export default function AdminLogin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [touched, setTouched] = useState({ username: false, password: false });
  const { login } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const usernameError = touched.username && !username.trim() ? "El usuario es obligatorio" : "";
  const passwordError = touched.password && !password.trim() ? "La contraseña es obligatoria" : "";
  const isValid = username.trim() && password.trim();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      navigate("/admin");
    } catch (err: any) {
      const msg = err?.response?.data?.error || "Error al iniciar sesión";
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "var(--space-lg)" }}>
      <div style={{ position: "absolute", top: "var(--space-lg)", right: "var(--space-lg)" }}>
        <ThemeToggle />
      </div>
      <Card style={{ width: "100%", maxWidth: 400, padding: "var(--space-xl)" }}>
        <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-lg)", textAlign: "center" }}>
          Acceso administración
        </h2>
        <form data-testid="admin-login-form" onSubmit={submit} style={{ display: "grid", gap: "var(--space-md)" }}>
          <Input
            data-testid="username-input"
            label="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, username: true }))}
            error={usernameError}
            autoComplete="username"
          />
          <Input
            data-testid="password-input"
            label="Contraseña"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, password: true }))}
            error={passwordError}
            autoComplete="current-password"
          />
          <Button data-testid="login-submit-btn" type="submit" disabled={loading || !isValid} fullWidth>
            {loading ? "Iniciando..." : "Iniciar sesión"}
          </Button>
        </form>
        {error && (
          <p data-testid="login-error-msg" role="alert" style={{ color: "var(--color-danger)", marginTop: "var(--space-md)", fontSize: "var(--font-size-sm)", textAlign: "center" }}>
            {error}
          </p>
        )}
      </Card>
    </div>
  );
}

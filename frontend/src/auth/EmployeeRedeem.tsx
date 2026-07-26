import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { Button, Input, Card, ThemeToggle } from "../components/ui";
import { useToast } from "../contexts/ToastContext";

export default function EmployeeRedeem() {
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [touched, setTouched] = useState(false);
  const { redeem } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const tokenError = touched && !token.trim() ? "El código de acceso es obligatorio" : "";
  const isValid = token.trim().length > 0;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;
    setError("");
    setLoading(true);
    try {
      await redeem(token);
      navigate("/employee");
    } catch (err: any) {
      const msg = err?.response?.data?.error || "Token inválido o expirado";
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
          Acceso empleado
        </h2>
        <form data-testid="employee-redeem-form" onSubmit={submit} style={{ display: "grid", gap: "var(--space-md)" }}>
          <Input
            data-testid="token-input"
            label="Código de acceso"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            onBlur={() => setTouched(true)}
            error={tokenError}
            placeholder="Introduce tu código"
          />
          <Button data-testid="redeem-submit-btn" type="submit" disabled={loading || !isValid} fullWidth>
            {loading ? "Verificando..." : "Acceder"}
          </Button>
        </form>
        {error && (
          <p data-testid="redeem-error-msg" role="alert" style={{ color: "var(--color-danger)", marginTop: "var(--space-md)", fontSize: "var(--font-size-sm)", textAlign: "center" }}>
            {error}
          </p>
        )}
      </Card>
    </div>
  );
}

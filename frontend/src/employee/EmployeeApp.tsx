import { useEffect, useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import ProtectedRoute from "../auth/ProtectedRoute";
import PdfReader from "../components/PdfReader";
import client from "../api/client";
import { Button, Card, Badge, EmptyState, ProgressBar, ThemeToggle, SkeletonCard } from "../components/ui";

interface Enrollment {
  id: number;
  course_id: number;
  course_title: string;
  status: string;
  attempts_used: number;
  score: number | null;
  total: number | null;
}

export default function EmployeeApp() {
  const { employee, logout } = useAuth();
  const navigate = useNavigate();
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadEnrollments();
  }, []);

  const loadEnrollments = async () => {
    setLoading(true);
    setError("");
    try {
      const r = await client.get<{ enrollments: Enrollment[] }>("/employee/enrollments");
      setEnrollments(r.data.enrollments);
    } catch (e: any) {
      setError(e?.response?.data?.error || "Error al cargar tus cursos");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/employee/redeem");
  };

  const getStatusVariant = (status: string): "success" | "warning" | "danger" | "neutral" => {
    switch (status) {
      case "completed": return "success";
      case "in_progress": return "warning";
      case "pending": return "neutral";
      case "failed": return "danger";
      default: return "neutral";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "completed": return "Completado";
      case "in_progress": return "En progreso";
      case "pending": return "Pendiente";
      case "failed": return "Fallido";
      default: return status;
    }
  };

  const getProgress = (enrollment: Enrollment): number => {
    if (enrollment.status === "completed") return 100;
    if (enrollment.status === "pending") return 0;
    if (enrollment.status === "failed") return 100;
    if (enrollment.score !== null && enrollment.total !== null && enrollment.total > 0) {
      return (enrollment.score / enrollment.total) * 100;
    }
    return enrollment.attempts_used > 0 ? 50 : 0;
  };

  return (
    <ProtectedRoute role="employee">
      <div data-testid="employee-app" style={{ minHeight: "100vh", background: "var(--color-bg)" }}>
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "var(--space-md) var(--space-lg)",
            borderBottom: "1px solid var(--color-border-light)",
            background: "var(--color-bg-secondary)",
          }}
        >
          <h1 style={{ fontSize: "var(--font-size-xl)" }}>Portal del empleado</h1>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-md)" }}>
            <span style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)" }}>
              Hola, {employee?.name}
            </span>
            <ThemeToggle />
            <Button variant="secondary" size="sm" onClick={handleLogout}>
              Salir
            </Button>
          </div>
        </header>

        <main style={{ padding: "var(--space-lg)", maxWidth: 800, margin: "0 auto" }}>
          <Routes>
            <Route
              path="read"
              element={
                <PdfReader
                  enrollmentId={0}
                  sectionId={0}
                  sectionBaseSeconds={0}
                  pdfUrl=""
                />
              }
            />
            <Route
              path="*"
              element={
                <div>
                  <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-lg)" }}>Mis cursos</h2>
                  {error && (
                    <p role="alert" aria-live="assertive" style={{ color: "var(--color-danger)", marginBottom: "var(--space-md)" }}>
                      {error}
                    </p>
                  )}
                  {loading ? (
                    <SkeletonCard count={3} />
                  ) : enrollments.length === 0 ? (
                    <EmptyState
                      data-testid="empty-state"
                      icon="🎓"
                      title="Aún no tienes formaciones asignadas"
                      description="Cuando tu administrador te asigne cursos de formación, aparecerán aquí."
                    />
                  ) : (
                    <div style={{ display: "grid", gap: "var(--space-md)" }}>
                      {enrollments.map((enrollment) => (
                        <Card key={enrollment.id} data-testid={`enrollment-card-${enrollment.id}`} hoverable>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "var(--space-md)" }}>
                            <div>
                              <h3 style={{ fontSize: "var(--font-size-lg)", marginBottom: "var(--space-xs)" }}>
                                {enrollment.course_title}
                              </h3>
                              <Badge variant={getStatusVariant(enrollment.status)} size="sm">
                                {getStatusLabel(enrollment.status)}
                              </Badge>
                            </div>
                            <Button
                              data-testid="continue-reading-btn"
                              size="sm"
                              onClick={() => navigate(`/employee/read?enrollment=${enrollment.id}`)}
                              disabled={enrollment.status === "completed"}
                            >
                              {enrollment.status === "completed" ? "Finalizado" : "Continuar"}
                            </Button>
                          </div>
                          <ProgressBar
                            value={getProgress(enrollment)}
                            label="Progreso"
                            showPercentage
                          />
                          {enrollment.score !== null && enrollment.total !== null && (
                            <p style={{ marginTop: "var(--space-sm)", fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
                              Puntuación: <strong>{enrollment.score}/{enrollment.total}</strong>
                            </p>
                          )}
                          <p style={{ marginTop: "var(--space-xs)", fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
                            Intentos utilizados: {enrollment.attempts_used}
                          </p>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              }
            />
          </Routes>
        </main>
      </div>
    </ProtectedRoute>
  );
}

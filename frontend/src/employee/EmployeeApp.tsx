import { useEffect, useState } from "react";
import { Routes, Route, useNavigate, useSearchParams } from "react-router-dom";
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
  version: number | null;
  cycle: number;
  active_seconds: number;
  attempts_used: number;
  score: number | null;
  total: number | null;
}

interface EnrollmentDetail {
  id: number;
  course_title: string;
  version: number | null;
  cycle: number;
  status: string;
  can_read: boolean;
  active_seconds: number;
  sections: Array<{
    id: number;
    order: number;
    title: string;
    content: string;
    has_pdf: boolean;
    accumulated_seconds: number;
    minimum_seconds: number;
    complete: boolean;
  }>;
}

function EnrollmentReader() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const enrollmentId = Number(params.get("enrollment"));
  const [detail, setDetail] = useState<EnrollmentDetail | null>(null);
  const [sectionIndex, setSectionIndex] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!enrollmentId) return;
    client.get<EnrollmentDetail>(`/employee/enrollments/${enrollmentId}`)
      .then((response) => setDetail(response.data))
      .catch((requestError) => setError(requestError?.response?.data?.error || "No se pudo cargar el curso"));
  }, [enrollmentId]);

  if (error) return <p role="alert" style={{ color: "var(--color-danger)" }}>{error}</p>;
  if (!detail) return <p style={{ color: "var(--color-text-muted)" }}>Cargando curso...</p>;
  const section = detail.sections[sectionIndex];
  if (!section) return <EmptyState title="Curso sin secciones" description="Contacta con administración." />;
  const apiBase = import.meta.env.VITE_API_BASE_URL || "/api";
  const pdfUrl = section.has_pdf
    ? `${apiBase}/employee/enrollments/${detail.id}/sections/${section.id}/pdf`
    : undefined;

  return (
    <div>
      <Button variant="ghost" size="sm" onClick={() => navigate("/employee")}>Volver a mis cursos</Button>
      <div style={{ margin: "var(--space-md) 0" }}>
        <h1 style={{ fontSize: "var(--font-size-2xl)" }}>{detail.course_title}</h1>
        <p style={{ color: "var(--color-text-secondary)" }}>Versión {detail.version || "-"} · Realización {detail.cycle} · Tiempo activo {detail.active_seconds}s</p>
      </div>
      <PdfReader
        enrollmentId={detail.id}
        sectionId={section.id}
        sectionOrder={section.order}
        title={section.title}
        content={section.content}
        minimumSeconds={section.minimum_seconds}
        accumulatedSeconds={section.accumulated_seconds}
        complete={section.complete}
        pdfUrl={pdfUrl}
        canRead={detail.can_read}
        onProgress={(progress) => setDetail((current) => current ? {
          ...current,
          active_seconds: current.active_seconds - section.accumulated_seconds + progress.accumulated,
          sections: current.sections.map((item) => item.id === section.id ? {
            ...item,
            accumulated_seconds: progress.accumulated,
            complete: progress.complete,
          } : item),
        } : current)}
      />
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "var(--space-md)" }}>
        <Button variant="secondary" onClick={() => setSectionIndex((index) => Math.max(0, index - 1))} disabled={sectionIndex === 0}>Sección anterior</Button>
        <Button onClick={() => setSectionIndex((index) => Math.min(detail.sections.length - 1, index + 1))} disabled={sectionIndex >= detail.sections.length - 1 || !section.complete}>Siguiente sección</Button>
      </div>
    </div>
  );
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
      case "passed": return "success";
      case "complete": return "success";
      case "in_progress": return "warning";
      case "paused": return "warning";
      case "assigned": return "neutral";
      case "cancelled": return "danger";
      case "failed_exhausted": return "danger";
      default: return "neutral";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "passed": return "Aprobado";
      case "complete": return "Lectura completada";
      case "in_progress": return "En progreso";
      case "paused": return "Pausado";
      case "assigned": return "Asignado";
      case "cancelled": return "Cancelado";
      case "failed_exhausted": return "Intentos agotados";
      default: return status;
    }
  };

  const getProgress = (enrollment: Enrollment): number => {
    if (["passed", "complete", "failed_exhausted"].includes(enrollment.status)) return 100;
    if (enrollment.status === "assigned") return 0;
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
              element={<EnrollmentReader />}
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
                              disabled={["passed", "failed_exhausted", "cancelled"].includes(enrollment.status)}
                            >
                              {["passed", "failed_exhausted", "cancelled"].includes(enrollment.status) ? "Finalizado" : "Continuar"}
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
                            Versión {enrollment.version || "-"} · Realización {enrollment.cycle} · Tiempo activo {enrollment.active_seconds}s
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

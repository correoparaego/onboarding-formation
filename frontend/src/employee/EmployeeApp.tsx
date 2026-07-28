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
  test_unlocked: boolean;
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

function ComprehensionTest({ enrollmentId, onFinished }: { enrollmentId: number; onFinished: () => void }) {
  const [questions, setQuestions] = useState<Array<{ id: number; text: string; options: string[] }>>([]);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [attempt, setAttempt] = useState(0);
  const [remaining, setRemaining] = useState(0);
  const [result, setResult] = useState<{ result: string; score: number; total: number; reading_reset?: boolean } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    client.get("/test/questions", { params: { enrollment_id: enrollmentId } })
      .then((response) => {
        setQuestions(response.data.questions);
        setAttempt(response.data.attempt_no);
        setRemaining(response.data.attempts_remaining);
      })
      .catch((requestError) => setError(requestError?.response?.data?.error || "No se pudo cargar el test"));
  }, [enrollmentId]);

  const submit = async () => {
    try {
      const response = await client.post("/test/submit", {
        enrollment_id: enrollmentId,
        answers: Object.entries(answers).map(([questionId, selectedIndex]) => ({
          question_id: Number(questionId),
          selected_index: selectedIndex,
        })),
      });
      setResult(response.data);
    } catch (requestError: any) {
      setError(requestError?.response?.data?.error || "No se pudo corregir el test");
    }
  };

  if (error) return <p role="alert" style={{ color: "var(--color-danger)" }}>{error}</p>;
  if (result) return (
    <Card>
      <h2>{result.result === "pass" ? "Test aprobado" : "Test no superado"}</h2>
      <p>Resultado: {result.score}/{result.total}</p>
      {result.reading_reset && <p>Debes completar de nuevo la lectura antes del siguiente intento.</p>}
      <Button onClick={onFinished}>Volver al curso</Button>
    </Card>
  );

  return (
    <Card>
      <h2>Test de comprensión</h2>
      <p>Intento {attempt}. Intentos disponibles: {remaining}.</p>
      {questions.map((question, questionIndex) => (
        <fieldset key={question.id} style={{ marginTop: "var(--space-md)", border: 0, padding: 0 }}>
          <legend style={{ fontWeight: 600 }}>{questionIndex + 1}. {question.text}</legend>
          {question.options.map((option, optionIndex) => (
            <label key={optionIndex} style={{ display: "block", padding: 6 }}>
              <input
                type="radio"
                name={`question-${question.id}`}
                checked={answers[question.id] === optionIndex}
                onChange={() => setAnswers({ ...answers, [question.id]: optionIndex })}
              /> {option}
            </label>
          ))}
        </fieldset>
      ))}
      <Button onClick={submit} disabled={!questions.length || Object.keys(answers).length !== questions.length} style={{ marginTop: "var(--space-md)" }}>
        Enviar respuestas
      </Button>
    </Card>
  );
}

function EnrollmentReader() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const enrollmentId = Number(params.get("enrollment"));
  const [detail, setDetail] = useState<EnrollmentDetail | null>(null);
  const [sectionIndex, setSectionIndex] = useState(0);
  const [showTest, setShowTest] = useState(false);
  const [error, setError] = useState("");

  const loadDetail = () => {
    if (!enrollmentId) return;
    client.get<EnrollmentDetail>(`/employee/enrollments/${enrollmentId}`)
      .then((response) => setDetail(response.data))
      .catch((requestError) => setError(requestError?.response?.data?.error || "No se pudo cargar el curso"));
  };

  useEffect(() => {
    loadDetail();
  }, [enrollmentId]);

  if (error) return <p role="alert" style={{ color: "var(--color-danger)" }}>{error}</p>;
  if (!detail) return <p style={{ color: "var(--color-text-muted)" }}>Cargando curso...</p>;
  if (!detail.can_read) return <Card>Este curso está pausado o cancelado. El contador y el contenido están bloqueados.</Card>;
  if (showTest) return <ComprehensionTest enrollmentId={detail.id} onFinished={() => {
    setShowTest(false);
    setSectionIndex(0);
    loadDetail();
  }} />;
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
          status: progress.testUnlocked ? "complete" : current.status,
          test_unlocked: progress.testUnlocked || current.test_unlocked,
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
      {detail.test_unlocked && (
        <Button onClick={() => setShowTest(true)} style={{ marginTop: "var(--space-md)", width: "100%" }}>
          Realizar test de comprensión
        </Button>
      )}
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

import { useEffect, useState } from "react";
import { coursesApi } from "../api/endpoints";
import { Button, Card, Badge, Input, EmptyState, ConfirmDialog, SkeletonTable, ResponsiveTable } from "../components/ui";
import { useToast } from "../contexts/ToastContext";
import Breadcrumb from "../components/layout/Breadcrumb";

interface Course {
  id: number;
  title: string;
  min_time_divisor: number;
  has_pdf: boolean;
  positions: string[];
  section_count: number;
  has_bank: boolean;
}

interface CourseDetail {
  id: number;
  title: string;
  min_time_divisor: number;
  positions: string[];
  sections: Array<{ order: number; section_base: number }>;
  banks: Array<{
    id: number;
    questions: Array<{ text: string; options: string[]; correct_index: number }>;
  }>;
}

export default function CourseManagement() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingCourse, setEditingCourse] = useState<CourseDetail | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [newMinDivisor, setNewMinDivisor] = useState(3);
  const [sections, setSections] = useState<Array<{ order: number; section_base: number }>>([
    { order: 1, section_base: 60 },
  ]);
  const [deleteTarget, setDeleteTarget] = useState<Course | null>(null);
  const toast = useToast();

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    setLoading(true);
    setError("");
    try {
      const r = await coursesApi.list();
      setCourses(r.data.courses as any);
    } catch (e: any) {
      setError(e?.response?.data?.error || "Error al cargar cursos");
    } finally {
      setLoading(false);
    }
  };

  const createCourse = async () => {
    if (!newTitle.trim()) return;
    try {
      await coursesApi.create({ title: newTitle, sections });
      setNewTitle("");
      setSections([{ order: 1, section_base: 60 }]);
      setShowForm(false);
      loadCourses();
      toast.success("Curso creado correctamente");
    } catch (e: any) {
      const msg = e?.response?.data?.error || "Error al crear curso";
      setError(msg);
      toast.error(msg);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    try {
      await coursesApi.delete(deleteTarget.id);
      setDeleteTarget(null);
      loadCourses();
      toast.success(`Curso "${deleteTarget.title}" eliminado`);
    } catch (e: any) {
      const msg = e?.response?.data?.error || "Error al eliminar curso";
      setError(msg);
      toast.error(msg);
    }
  };

  const viewCourse = async (id: number) => {
    try {
      const r = await coursesApi.detail(id);
      setEditingCourse(r.data);
    } catch (e: any) {
      setError(e?.response?.data?.error || "Error al cargar detalles del curso");
    }
  };

  const addSection = () => {
    setSections([...sections, { order: sections.length + 1, section_base: 60 }]);
  };

  const removeSection = (index: number) => {
    setSections(sections.filter((_, i) => i !== index));
  };

  const updateSection = (index: number, field: "order" | "section_base", value: number) => {
    const updated = [...sections];
    updated[index][field] = value;
    setSections(updated);
  };

  const tableColumns = [
    { key: "title", label: "Título" },
    {
      key: "has_pdf",
      label: "PDF",
      render: (row: Course) => (
        <Badge variant={row.has_pdf ? "success" : "neutral"} size="sm">
          {row.has_pdf ? "✓" : "✗"}
        </Badge>
      ),
    },
    { key: "section_count", label: "Secciones" },
    {
      key: "has_bank",
      label: "Test",
      render: (row: Course) => (
        <Badge variant={row.has_bank ? "success" : "neutral"} size="sm">
          {row.has_bank ? "✓" : "✗"}
        </Badge>
      ),
    },
    {
      key: "positions",
      label: "Posiciones",
      render: (row: Course) => (
        <span style={{ fontSize: "var(--font-size-sm)" }}>
          {row.positions.join(", ") || "-"}
        </span>
      ),
    },
    {
      key: "actions",
      label: "Acciones",
      render: (row: Course) => (
        <div style={{ display: "flex", gap: "var(--space-sm)", justifyContent: "center" }}>
          <Button variant="ghost" size="sm" onClick={() => viewCourse(row.id)}>
            Ver
          </Button>
          <Button
            data-testid="delete-course-btn"
            variant="ghost"
            size="sm"
            onClick={() => setDeleteTarget(row)}
            style={{ color: "var(--color-danger)" }}
          >
            Eliminar
          </Button>
        </div>
      ),
    },
  ];

  if (loading) {
    return (
      <div>
        <Breadcrumb items={[{ label: "Inicio", to: "/admin/dashboard" }, { label: "Cursos" }]} />
        <SkeletonTable rows={4} cols={4} />
      </div>
    );
  }

  return (
    <div data-testid="courses-page">
      <Breadcrumb items={[{ label: "Inicio", to: "/admin/dashboard" }, { label: "Cursos" }]} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-md)" }}>
        <h2 style={{ fontSize: "var(--font-size-2xl)" }}>Gestión de cursos</h2>
        <Button data-testid="create-course-btn" variant={showForm ? "secondary" : "primary"} onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancelar" : "+ Nuevo curso"}
        </Button>
      </div>

      {error && (
        <p role="alert" aria-live="assertive" style={{ color: "var(--color-danger)", marginBottom: "var(--space-md)" }}>
          {error}
        </p>
      )}

      {showForm && (
        <Card data-testid="create-course-form" style={{ background: "var(--color-bg-secondary)", marginBottom: "var(--space-lg)" }}>
          <h3 style={{ marginBottom: "var(--space-md)" }}>Crear nuevo curso</h3>
          <div style={{ display: "grid", gap: "var(--space-md)" }}>
            <Input
              data-testid="course-title-input"
              label="Título del curso"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Ej: Seguridad en el trabajo"
            />
            <div>
              <Input
                label="Divisor de tiempo mínimo"
                type="number"
                min="1"
                value={String(newMinDivisor)}
                onChange={(e) => setNewMinDivisor(Number(e.target.value))}
                style={{ width: 100 }}
                hint="Tiempo mínimo por sección = tiempo_base / divisor"
              />
            </div>
            <div>
              <label style={{ fontSize: "var(--font-size-sm)", fontWeight: 500, display: "block", marginBottom: "var(--space-xs)" }}>
                Secciones
              </label>
              {sections.map((section, i) => (
                <div key={i} style={{ display: "flex", gap: "var(--space-sm)", marginTop: "var(--space-sm)", alignItems: "center" }}>
                  <input
                    type="number"
                    placeholder="Orden"
                    value={section.order}
                    onChange={(e) => updateSection(i, "order", Number(e.target.value))}
                    style={{ width: 80 }}
                  />
                  <input
                    type="number"
                    placeholder="Tiempo base (s)"
                    value={section.section_base}
                    onChange={(e) => updateSection(i, "section_base", Number(e.target.value))}
                    style={{ width: 120 }}
                  />
                  <span style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>segundos</span>
                  {sections.length > 1 && (
                    <button
                      onClick={() => removeSection(i)}
                      aria-label="Eliminar sección"
                      style={{ padding: "var(--space-xs) var(--space-sm)", color: "var(--color-danger)", cursor: "pointer", background: "none", border: "none" }}
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
              <Button variant="ghost" size="sm" onClick={addSection} style={{ marginTop: "var(--space-sm)" }}>
                + Añadir sección
              </Button>
            </div>
            <Button data-testid="course-submit-btn" onClick={createCourse} disabled={!newTitle.trim()}>
              Crear curso
            </Button>
          </div>
        </Card>
      )}

      {editingCourse && (
        <Card style={{ marginBottom: "var(--space-lg)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "var(--space-md)" }}>
            <h3>{editingCourse.title}</h3>
            <Button variant="ghost" size="sm" onClick={() => setEditingCourse(null)}>Cerrar</Button>
          </div>
          <p style={{ marginBottom: "var(--space-sm)" }}>
            <strong>Divisor de tiempo:</strong> {editingCourse.min_time_divisor}
          </p>
          <p style={{ marginBottom: "var(--space-md)" }}>
            <strong>Posiciones:</strong> {editingCourse.positions.join(", ") || "Ninguna"}
          </p>
          <h4 style={{ marginBottom: "var(--space-sm)" }}>Secciones ({editingCourse.sections.length})</h4>
          {editingCourse.sections.length > 0 ? (
            <ul style={{ marginBottom: "var(--space-md)", paddingLeft: "var(--space-lg)" }}>
              {editingCourse.sections.map((s, i) => (
                <li key={i} style={{ marginBottom: "var(--space-xs)" }}>
                  Sección {s.order}: {s.section_base}s (mínimo: {Math.ceil(s.section_base / editingCourse.min_time_divisor)}s)
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: "var(--color-text-muted)", marginBottom: "var(--space-md)" }}>Sin secciones</p>
          )}
          <h4 style={{ marginBottom: "var(--space-sm)" }}>Bancos de preguntas ({editingCourse.banks.length})</h4>
          {editingCourse.banks.length > 0 ? (
            editingCourse.banks.map((bank, i) => (
              <div key={i} style={{ marginBottom: "var(--space-md)" }}>
                <strong>Banco #{bank.id}</strong> ({bank.questions.length} preguntas)
                <ol style={{ marginTop: "var(--space-sm)", paddingLeft: "var(--space-lg)" }}>
                  {bank.questions.map((q, j) => (
                    <li key={j} style={{ marginBottom: "var(--space-sm)" }}>
                      <div>{q.text}</div>
                      <ul style={{ marginTop: "var(--space-xs)", paddingLeft: "var(--space-lg)", listStyle: "none", padding: 0 }}>
                        {q.options.map((opt, k) => (
                          <li
                            key={k}
                            style={{
                              fontWeight: k === q.correct_index ? "bold" : "normal",
                              color: k === q.correct_index ? "var(--color-success)" : "inherit",
                            }}
                          >
                            {opt} {k === q.correct_index && "✓"}
                          </li>
                        ))}
                      </ul>
                    </li>
                  ))}
                </ol>
              </div>
            ))
          ) : (
            <p style={{ color: "var(--color-text-muted)" }}>Sin bancos de preguntas</p>
          )}
        </Card>
      )}

      {courses.length === 0 ? (
        <EmptyState
          icon="📚"
          title="No hay cursos creados"
          description="Haz clic en '+ Nuevo curso' para crear tu primer curso de formación."
          action={
            <Button onClick={() => setShowForm(true)}>+ Nuevo curso</Button>
          }
        />
      ) : (
        <ResponsiveTable columns={tableColumns} data={courses} data-testid="courses-table" rowTestIdKey="id" rowTestIdPrefix="course-row" />
      )}

      <ConfirmDialog
        data-testid="confirm-dialog"
        isOpen={!!deleteTarget}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
        title="Eliminar curso"
        message={`¿Eliminar "${deleteTarget?.title}"? Esta acción no se puede deshacer.`}
        confirmLabel="Eliminar"
        danger
      />
    </div>
  );
}

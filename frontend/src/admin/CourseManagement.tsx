import { useEffect, useState } from "react";
import { coursesApi, CourseSectionPayload, CourseVersionPayload } from "../api/endpoints";
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
  positions: Array<{ id: number; name: string }>;
  active_version: CourseVersionPayload | null;
  editing_version: CourseVersionPayload | null;
  sections: CourseSectionPayload[];
  banks: Array<{
    id: number;
    questions: Array<{ text: string; options: string[]; correct_index: number }>;
  }>;
}

interface EditableSection extends CourseSectionPayload {
  file?: File | null;
}

export default function CourseManagement() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingCourse, setEditingCourse] = useState<CourseDetail | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [newMinDivisor, setNewMinDivisor] = useState(3);
  const [sections, setSections] = useState<EditableSection[]>([
    { order: 1, title: "", content: "", section_base: 60, file: null },
  ]);
  const [positions, setPositions] = useState<Array<{ id: number; name: string }>>([]);
  const [selectedPositionIds, setSelectedPositionIds] = useState<number[]>([]);
  const [editingVersion, setEditingVersion] = useState<CourseVersionPayload | null>(null);
  const [editSections, setEditSections] = useState<EditableSection[]>([]);
  const [deleteTarget, setDeleteTarget] = useState<Course | null>(null);
  const toast = useToast();

  useEffect(() => {
    loadCourses();
    coursesApi.positions().then((response) => setPositions(response.data.positions));
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
      const created = await coursesApi.create({
        title: newTitle,
        min_time_divisor: newMinDivisor,
        position_ids: selectedPositionIds,
        sections: sections.map(({ file: _file, ...section }) => section),
      });
      const detail = await coursesApi.detail(created.data.id);
      for (const section of sections) {
        const persisted = detail.data.sections.find((item) => item.order === section.order);
        if (section.file && persisted?.id) {
          await coursesApi.uploadSectionPdf(persisted.id, section.file);
        }
      }
      setNewTitle("");
      setSections([{ order: 1, title: "", content: "", section_base: 60, file: null }]);
      setSelectedPositionIds([]);
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
    setSections([
      ...sections,
      { order: sections.length + 1, title: "", content: "", section_base: 60, file: null },
    ]);
  };

  const removeSection = (index: number) => {
    setSections(sections.filter((_, i) => i !== index));
  };

  const updateSection = (index: number, updates: Partial<EditableSection>) => {
    const updated = [...sections];
    updated[index] = { ...updated[index], ...updates };
    setSections(updated);
  };

  const startEditingVersion = async () => {
    if (!editingCourse) return;
    try {
      const response = await coursesApi.createDraft(editingCourse.id);
      setEditingVersion(response.data.version);
      setEditSections(response.data.version.sections);
    } catch (e: any) {
      toast.error(e?.response?.data?.error || "Error al crear el borrador");
    }
  };

  const saveAndPublishVersion = async () => {
    if (!editingCourse || !editingVersion) return;
    try {
      const updated = await coursesApi.updateVersion(editingVersion.id, {
        title: editingVersion.title,
        min_time_divisor: editingVersion.min_time_divisor,
        position_ids: editingCourse.positions.map((position) => position.id),
        sections: editSections.map(({ file: _file, ...section }) => section),
      });
      for (const section of editSections) {
        const persisted = updated.data.version.sections.find((item) => item.order === section.order);
        if (section.file && persisted?.id) {
          await coursesApi.uploadSectionPdf(persisted.id, section.file);
        }
      }
      await coursesApi.publishVersion(editingVersion.id);
      toast.success("Nueva versión publicada");
      setEditingVersion(null);
      await viewCourse(editingCourse.id);
      loadCourses();
    } catch (e: any) {
      toast.error(e?.response?.data?.error || "Error al publicar la versión");
    }
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
              <label style={{ fontSize: "var(--font-size-sm)", fontWeight: 500 }}>Puestos aplicables</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-sm)", marginTop: "var(--space-xs)" }}>
                {positions.map((position) => (
                  <label key={position.id} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <input
                      type="checkbox"
                      checked={selectedPositionIds.includes(position.id)}
                      onChange={(event) => setSelectedPositionIds(
                        event.target.checked
                          ? [...selectedPositionIds, position.id]
                          : selectedPositionIds.filter((id) => id !== position.id)
                      )}
                    />
                    {position.name}
                  </label>
                ))}
              </div>
            </div>
            <div>
              <label style={{ fontSize: "var(--font-size-sm)", fontWeight: 500, display: "block", marginBottom: "var(--space-xs)" }}>
                Secciones
              </label>
              {sections.map((section, i) => (
                <Card key={i} style={{ marginTop: "var(--space-sm)", padding: "var(--space-md)" }}>
                  <div style={{ display: "grid", gridTemplateColumns: "80px 1fr 130px", gap: "var(--space-sm)" }}>
                    <input type="number" aria-label="Orden" value={section.order} onChange={(e) => updateSection(i, { order: Number(e.target.value) })} />
                    <input placeholder="Título de la sección" value={section.title} onChange={(e) => updateSection(i, { title: e.target.value })} />
                    <input type="number" aria-label="Tiempo base en segundos" value={section.section_base} onChange={(e) => updateSection(i, { section_base: Number(e.target.value) })} />
                  </div>
                  <textarea
                    placeholder="Texto editable de la sección"
                    value={section.content}
                    onChange={(e) => updateSection(i, { content: e.target.value })}
                    rows={5}
                    style={{ width: "100%", marginTop: "var(--space-sm)" }}
                  />
                  <label style={{ display: "block", marginTop: "var(--space-sm)", fontSize: "var(--font-size-sm)" }}>
                    PDF complementario (máximo 25 MB)
                    <input type="file" accept="application/pdf,.pdf" onChange={(e) => updateSection(i, { file: e.target.files?.[0] || null })} style={{ display: "block", marginTop: 6 }} />
                  </label>
                  {sections.length > 1 && (
                    <button
                      onClick={() => removeSection(i)}
                      aria-label="Eliminar sección"
                      style={{ padding: "var(--space-xs) var(--space-sm)", color: "var(--color-danger)", cursor: "pointer", background: "none", border: "none" }}
                    >
                      ✕
                    </button>
                  )}
                </Card>
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
            <strong>Posiciones:</strong> {editingCourse.positions.map((position) => position.name).join(", ") || "Ninguna"}
          </p>
          {!editingVersion ? (
            <Button onClick={startEditingVersion} style={{ marginBottom: "var(--space-md)" }}>
              Crear nueva versión
            </Button>
          ) : (
            <Card style={{ marginBottom: "var(--space-lg)", background: "var(--color-bg-secondary)" }}>
              <h4 style={{ marginBottom: "var(--space-sm)" }}>Borrador v{editingVersion.number}</h4>
              <Input label="Título" value={editingVersion.title} onChange={(event) => setEditingVersion({ ...editingVersion, title: event.target.value })} />
              {editSections.map((section, index) => (
                <div key={section.id || index} style={{ marginTop: "var(--space-md)", paddingTop: "var(--space-md)", borderTop: "1px solid var(--color-border)" }}>
                  <Input label={`Sección ${index + 1}`} value={section.title} onChange={(event) => setEditSections(editSections.map((item, itemIndex) => itemIndex === index ? { ...item, title: event.target.value } : item))} />
                  <textarea
                    value={section.content}
                    onChange={(event) => setEditSections(editSections.map((item, itemIndex) => itemIndex === index ? { ...item, content: event.target.value } : item))}
                    rows={5}
                    style={{ width: "100%", marginTop: "var(--space-sm)" }}
                  />
                  <label style={{ display: "block", marginTop: "var(--space-sm)", fontSize: "var(--font-size-sm)" }}>
                    {section.has_pdf ? "Sustituir PDF" : "Añadir PDF"}
                    <input type="file" accept="application/pdf,.pdf" onChange={(event) => setEditSections(editSections.map((item, itemIndex) => itemIndex === index ? { ...item, file: event.target.files?.[0] || null } : item))} style={{ display: "block", marginTop: 6 }} />
                  </label>
                </div>
              ))}
              <Button onClick={saveAndPublishVersion} style={{ marginTop: "var(--space-md)" }}>
                Guardar y publicar versión
              </Button>
            </Card>
          )}
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

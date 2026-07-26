import { useEffect, useState } from "react";
import { aiApi, banksApi, coursesApi } from "../../api/endpoints";
import { Button, Card } from "../../components/ui";
import { useToast } from "../../contexts/ToastContext";

export default function PdfTestGen() {
  const [file, setFile] = useState<File | null>(null);
  const [pdfText, setPdfText] = useState("");
  const [courseId, setCourseId] = useState<number | "">("");
  const [courses, setCourses] = useState<Array<{ id: number; title: string }>>([]);
  const [draft, setDraft] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [coursesLoading, setCoursesLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    coursesApi
      .list()
      .then((r) => setCourses(r.data.courses))
      .catch((e) => toast.error(e?.response?.data?.error || "Error al cargar cursos"))
      .finally(() => setCoursesLoading(false));
  }, []);

  const generate = async () => {
    setLoading(true);
    try {
      let r;
      if (file) {
        const form = new FormData();
        form.append("file", file);
        r = await aiApi.generateTests(form);
      } else {
        r = await aiApi.generateTestsText({ pdf_text: pdfText });
      }
      setDraft(r.data.draft);
    } catch (e: any) {
      toast.error(e?.response?.data?.error || "Error al generar el test.");
    } finally {
      setLoading(false);
    }
  };

  const save = async () => {
    if (!draft || courseId === "") return;
    setSaving(true);
    try {
      await banksApi.create({
        course_id: Number(courseId),
        questions: draft.questions.map((q: any) => ({
          text: q.text,
          options: q.options,
          correct_index: q.correct_index,
        })),
      });
      toast.success("Banco de preguntas guardado.");
      setDraft(null);
    } catch (e: any) {
      toast.error(e?.response?.data?.error || "Error al guardar el banco (¿varias respuestas correctas?).");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div data-testid="pdf-test-gen-page">
      <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-lg)" }}>Generar test desde PDF (IA)</h2>
      <Card style={{ maxWidth: 520, marginBottom: "var(--space-lg)" }}>
        <div style={{ display: "grid", gap: "var(--space-md)" }}>
          <div>
            <label htmlFor="pdfFile" style={{ display: "block", fontSize: "var(--font-size-sm)", fontWeight: 500, marginBottom: "var(--space-xs)" }}>
              Archivo PDF
            </label>
            <input
              id="pdfFile"
              data-testid="pdf-file-input"
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>
          <div>
            <label htmlFor="pdfText" style={{ display: "block", fontSize: "var(--font-size-sm)", fontWeight: 500, marginBottom: "var(--space-xs)" }}>
              O, pega el texto extraído del PDF
            </label>
            <textarea
              id="pdfText"
              rows={5}
              value={pdfText}
              onChange={(e) => setPdfText(e.target.value)}
              style={{ width: "100%", resize: "vertical" }}
            />
          </div>
          <Button data-testid="generate-tests-btn" onClick={generate} disabled={loading || (!file && !pdfText)}>
            {loading ? "Generando..." : "Generar borrador de test"}
          </Button>
        </div>
      </Card>
      {draft && (
        <Card style={{ maxWidth: 520 }}>
          <h3 style={{ marginBottom: "var(--space-md)" }}>Preguntas (revisa antes de guardar)</h3>
          {draft.questions && draft.questions.length > 0 && (
            <ol style={{ paddingLeft: "var(--space-lg)" }}>
              {draft.questions.map((q: any, i: number) => (
                <li key={i} style={{ marginBottom: "var(--space-md)" }}>
                  <strong>{q.text}</strong>
                  <ul style={{ listStyle: "none", padding: 0, marginTop: "var(--space-xs)" }}>
                    {q.options?.map((opt: string, j: number) => (
                      <li
                        key={j}
                        style={{
                          fontWeight: j === q.correct_index ? "bold" : "normal",
                          color: j === q.correct_index ? "var(--color-success)" : "inherit",
                        }}
                      >
                        {opt} {j === q.correct_index && " ✓"}
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ol>
          )}
          <details style={{ marginTop: "var(--space-md)" }}>
            <summary style={{ cursor: "pointer", color: "var(--color-primary)" }}>Ver JSON completo</summary>
            <pre style={{ fontSize: "var(--font-size-xs)", maxHeight: 300, overflow: "auto", marginTop: "var(--space-sm)", background: "var(--color-bg-secondary)", padding: "var(--space-md)", borderRadius: "var(--radius-sm)" }}>
              {JSON.stringify(draft, null, 2)}
            </pre>
          </details>
          <div style={{ marginTop: "var(--space-md)", display: "grid", gap: "var(--space-sm)" }}>
            <label htmlFor="courseSelect" style={{ fontSize: "var(--font-size-sm)", fontWeight: 500 }}>
              Curso destino
            </label>
            <select
              id="courseSelect"
              value={courseId}
              onChange={(e) => setCourseId(e.target.value ? Number(e.target.value) : "")}
              disabled={coursesLoading}
            >
              <option value="">-- selecciona --</option>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
          </div>
          <Button onClick={save} disabled={saving || courseId === ""} style={{ marginTop: "var(--space-md)" }}>
            {saving ? "Guardando..." : "Guardar banco"}
          </Button>
        </Card>
      )}
    </div>
  );
}

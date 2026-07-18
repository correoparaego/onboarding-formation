import { useEffect, useState } from "react";
import { aiApi, banksApi, coursesApi } from "../../api/endpoints";

// PDF -> test generation (spec ai-generation §PDF). The backend extracts PDF
// text server-side and returns a QuestionBank DRAFT (single-correct enforced).
// It is NOT persisted until the admin confirms "Guardar banco". Multi-correct
// drafts are rejected at save by the server.
export default function PdfTestGen() {
  const [file, setFile] = useState<File | null>(null);
  const [pdfText, setPdfText] = useState("");
  const [courseId, setCourseId] = useState<number | "">("");
  const [courses, setCourses] = useState<Array<{ id: number; title: string }>>([]);
  const [draft, setDraft] = useState<any>(null);
  const [err, setErr] = useState("");
  const [saved, setSaved] = useState("");

  useEffect(() => {
    coursesApi.list().then((r) => setCourses(r.data.courses)).catch(() => setCourses([]));
  }, []);

  const generate = async () => {
    setErr("");
    setSaved("");
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
      setErr(e?.response?.data?.error || "Error al generar el test.");
    }
  };

  const save = async () => {
    if (!draft || courseId === "") return;
    try {
      await banksApi.create({
        course_id: Number(courseId),
        questions: draft.questions.map((q: any) => ({
          text: q.text,
          options: q.options,
          correct_index: q.correct_index,
        })),
      });
      setSaved("Banco de preguntas guardado.");
      setDraft(null);
    } catch (e: any) {
      setErr(e?.response?.data?.error || "Error al guardar el banco (¿varias respuestas correctas?).");
    }
  };

  return (
    <div>
      <h2>Generar test desde PDF (IA)</h2>
      <div style={{ display: "grid", gap: 8, maxWidth: 520 }}>
        <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <label>O, pega el texto extraído del PDF</label>
        <textarea rows={5} value={pdfText} onChange={(e) => setPdfText(e.target.value)} />
        <button onClick={generate} disabled={!file && !pdfText}>Generar borrador de test</button>
      </div>
      {err && <p style={{ color: "red" }}>{err}</p>}
      {draft && (
        <div style={{ marginTop: 16, border: "1px solid #ccc", padding: 12 }}>
          <h3>Preguntas (revisa antes de guardar)</h3>
          <pre>{JSON.stringify(draft, null, 2)}</pre>
          <label>Curso destino</label>
          <select value={courseId} onChange={(e) => setCourseId(e.target.value ? Number(e.target.value) : "")}>
            <option value="">-- selecciona --</option>
            {courses.map((c) => (
              <option key={c.id} value={c.id}>{c.title}</option>
            ))}
          </select>
          <button onClick={save} disabled={courseId === ""}>Guardar banco</button>
        </div>
      )}
      {saved && <p style={{ color: "green" }}>{saved}</p>}
    </div>
  );
}

import { useState } from "react";
import { aiApi, coursesApi } from "../../api/endpoints";

// Guided course-content generation (spec ai-generation §Guided). The backend
// returns a DRAFT that is NOT persisted. The admin reviews/edits it here and
// only on explicit "Guardar como curso" is it written via POST /api/courses/.
export default function GuidedContent() {
  const [title, setTitle] = useState("");
  const [answers, setAnswers] = useState<Record<string, string>>({ objetivo: "" });
  const [refs, setRefs] = useState("");
  const [draft, setDraft] = useState<any>(null);
  const [err, setErr] = useState("");
  const [saved, setSaved] = useState("");

  const generate = async () => {
    setErr("");
    setSaved("");
    try {
      const r = await aiApi.generateContent({
        course_title: title,
        answers,
        reference_docs: refs.split("\n\n").map((s) => s.trim()).filter(Boolean),
      });
      setDraft(r.data.draft);
    } catch (e: any) {
      setErr(e?.response?.data?.error || "Error al generar contenido.");
    }
  };

  const save = async () => {
    if (!draft) return;
    try {
      await coursesApi.create({
        title: draft.title || title,
        sections: (draft.sections || []).map((s: any, i: number) => ({
          order: s.order ?? i + 1,
          section_base: s.section_base ?? 120,
        })),
      });
      setSaved("Curso guardado. Revisa las secciones en Cursos.");
      setDraft(null);
    } catch (e: any) {
      setErr(e?.response?.data?.error || "Error al guardar el curso.");
    }
  };

  return (
    <div>
      <h2>Generar contenido de curso (IA)</h2>
      <div style={{ display: "grid", gap: 8, maxWidth: 520 }}>
        <input placeholder="Título del curso" value={title} onChange={(e) => setTitle(e.target.value)} />
        <label>Preguntas guía (clave: valor)</label>
        {Object.entries(answers).map(([k, v]) => (
          <div key={k} style={{ display: "flex", gap: 8 }}>
            <input value={k} disabled />
            <input value={v} onChange={(e) => setAnswers((a) => ({ ...a, [k]: e.target.value }))} />
          </div>
        ))}
        <label>Documentos de referencia (separa con línea en blanco)</label>
        <textarea rows={5} value={refs} onChange={(e) => setRefs(e.target.value)} />
        <button onClick={generate} disabled={!title}>Generar borrador</button>
      </div>
      {err && <p style={{ color: "red" }}>{err}</p>}
      {draft && (
        <div style={{ marginTop: 16, border: "1px solid #ccc", padding: 12 }}>
          <h3>Borrador (revisa antes de guardar)</h3>
          <pre>{JSON.stringify(draft, null, 2)}</pre>
          <button onClick={save}>Guardar como curso</button>
        </div>
      )}
      {saved && <p style={{ color: "green" }}>{saved}</p>}
    </div>
  );
}

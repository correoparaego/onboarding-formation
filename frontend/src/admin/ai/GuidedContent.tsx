import { useState, useEffect, useRef, useCallback } from "react";
import { aiApi, coursesApi } from "../../api/endpoints";
import { Button, Input, Card } from "../../components/ui";
import { useToast } from "../../contexts/ToastContext";

const DRAFT_KEY = "guided-content-draft";

interface DraftData {
  title: string;
  answers: Record<string, string>;
  refs: string;
  savedAt: string;
}

export default function GuidedContent() {
  const [title, setTitle] = useState("");
  const [answers, setAnswers] = useState<Record<string, string>>({ objetivo: "" });
  const [refs, setRefs] = useState("");
  const [draft, setDraft] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [autoSaveIndicator, setAutoSaveIndicator] = useState<string | null>(null);
  const [hasRestoredDraft, setHasRestoredDraft] = useState(false);
  const toast = useToast();
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Restore draft from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(DRAFT_KEY);
      if (stored) {
        const data: DraftData = JSON.parse(stored);
        setHasRestoredDraft(true);
        setAutoSaveIndicator(`Borrador del ${new Date(data.savedAt).toLocaleString("es-ES")}`);
        // Store for restoration if user accepts
        (window as any).__pendingDraft = data;
      }
    } catch { /* ignore corrupt data */ }
  }, []);

  const restoreDraft = () => {
    const data = (window as any).__pendingDraft as DraftData | undefined;
    if (data) {
      setTitle(data.title);
      setAnswers(data.answers);
      setRefs(data.refs);
      setHasRestoredDraft(false);
      (window as any).__pendingDraft = null;
      toast.success("Borrador restaurado");
    }
  };

  const discardDraft = () => {
    localStorage.removeItem(DRAFT_KEY);
    setHasRestoredDraft(false);
    setAutoSaveIndicator(null);
    (window as any).__pendingDraft = null;
  };

  // Debounced auto-save to localStorage
  const autoSave = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      if (title || refs || Object.values(answers).some(v => v)) {
        const data: DraftData = { title, answers, refs, savedAt: new Date().toISOString() };
        localStorage.setItem(DRAFT_KEY, JSON.stringify(data));
        setAutoSaveIndicator("Borrador guardado");
        setTimeout(() => setAutoSaveIndicator(null), 2000);
      }
    }, 500);
  }, [title, answers, refs]);

  // Trigger auto-save on every change
  useEffect(() => { autoSave(); }, [title, answers, refs, autoSave]);

  const generate = async () => {
    setLoading(true);
    try {
      const r = await aiApi.generateContent({
        course_title: title,
        answers,
        reference_docs: refs.split("\n\n").map((s) => s.trim()).filter(Boolean),
      });
      setDraft(r.data.draft);
    } catch (e: any) {
      toast.error(e?.response?.data?.error || "Error al generar contenido.");
    } finally {
      setLoading(false);
    }
  };

  const save = async () => {
    if (!draft) return;
    setSaving(true);
    try {
      await coursesApi.create({
        title: draft.title || title,
        sections: (draft.sections || []).map((s: any, i: number) => ({
          order: s.order ?? i + 1,
          section_base: s.section_base ?? 120,
        })),
      });
      toast.success("Curso guardado. Revisa las secciones en Cursos.");
      setDraft(null);
      localStorage.removeItem(DRAFT_KEY);
      setAutoSaveIndicator(null);
    } catch (e: any) {
      toast.error(e?.response?.data?.error || "Error al guardar el curso.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div data-testid="guided-content-page">
      <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-lg)" }}>Generar contenido de curso (IA)</h2>

      {hasRestoredDraft && (
        <Card style={{ maxWidth: 520, marginBottom: "var(--space-md)", borderColor: "var(--color-warning)", border: "1px solid var(--color-warning)" }}>
          <p style={{ marginBottom: "var(--space-sm)" }}>Se encontró un borrador guardado previamente. ¿Deseas restaurarlo?</p>
          <div style={{ display: "flex", gap: "var(--space-sm)" }}>
            <Button variant="primary" size="sm" onClick={restoreDraft}>Restaurar</Button>
            <Button variant="ghost" size="sm" onClick={discardDraft}>Descartar</Button>
          </div>
        </Card>
      )}

      {autoSaveIndicator && !hasRestoredDraft && (
        <p style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)", marginBottom: "var(--space-sm)", textAlign: "right", maxWidth: 520 }}>
          ✓ {autoSaveIndicator}
        </p>
      )}

      <Card style={{ maxWidth: 520, marginBottom: "var(--space-lg)" }}>
        <div style={{ display: "grid", gap: "var(--space-md)" }}>
          <Input
            data-testid="course-title-input"
            label="Título del curso"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <div>
            <label style={{ display: "block", fontSize: "var(--font-size-sm)", fontWeight: 500, marginBottom: "var(--space-xs)" }}>
              Preguntas guía (clave: valor)
            </label>
            {Object.entries(answers).map(([k, v]) => (
              <div key={k} style={{ display: "flex", gap: "var(--space-sm)", marginBottom: "var(--space-xs)" }}>
                <input value={k} disabled aria-label={`Clave: ${k}`} style={{ flex: "0 0 120px" }} />
                <input
                  value={v}
                  onChange={(e) => setAnswers((a) => ({ ...a, [k]: e.target.value }))}
                  aria-label={`Valor para ${k}`}
                  style={{ flex: 1 }}
                />
              </div>
            ))}
          </div>
          <div>
            <label htmlFor="refs" style={{ display: "block", fontSize: "var(--font-size-sm)", fontWeight: 500, marginBottom: "var(--space-xs)" }}>
              Documentos de referencia (separa con línea en blanco)
            </label>
            <textarea
              id="refs"
              rows={5}
              value={refs}
              onChange={(e) => setRefs(e.target.value)}
              style={{ width: "100%", resize: "vertical" }}
            />
          </div>
          <Button data-testid="generate-btn" onClick={generate} disabled={loading || !title}>
            {loading ? "Generando..." : "Generar borrador"}
          </Button>
        </div>
      </Card>
      {draft && (
        <Card data-testid="draft-preview" style={{ maxWidth: 520 }}>
          <h3 style={{ marginBottom: "var(--space-md)" }}>Borrador (revisa antes de guardar)</h3>
          {draft.title && <h4 style={{ marginBottom: "var(--space-sm)" }}>{draft.title}</h4>}
          {draft.sections && draft.sections.length > 0 && (
            <div style={{ marginBottom: "var(--space-md)" }}>
              <strong>Secciones:</strong>
              <ul style={{ paddingLeft: "var(--space-lg)", marginTop: "var(--space-xs)" }}>
                {draft.sections.map((s: any, i: number) => (
                  <li key={i} style={{ marginBottom: "var(--space-xs)" }}>
                    <strong>Sección {s.order ?? i + 1}:</strong> {s.title || s.content || JSON.stringify(s)}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <details style={{ marginTop: "var(--space-md)" }}>
            <summary style={{ cursor: "pointer", color: "var(--color-primary)" }}>Ver JSON completo</summary>
            <pre style={{ fontSize: "var(--font-size-xs)", maxHeight: 300, overflow: "auto", marginTop: "var(--space-sm)", background: "var(--color-bg-secondary)", padding: "var(--space-md)", borderRadius: "var(--radius-sm)" }}>
              {JSON.stringify(draft, null, 2)}
            </pre>
          </details>
          <Button data-testid="save-course-btn" onClick={save} disabled={saving} style={{ marginTop: "var(--space-md)" }}>
            {saving ? "Guardando..." : "Guardar como curso"}
          </Button>
        </Card>
      )}
    </div>
  );
}

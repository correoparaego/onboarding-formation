import { useEffect, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";

import client from "../../api/client";
import { Button, Card } from "../ui";

import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export interface PdfReaderProps {
  enrollmentId: number;
  sectionId: number;
  sectionOrder?: number;
  title?: string;
  content?: string;
  minimumSeconds?: number;
  sectionBaseSeconds?: number;
  accumulatedSeconds?: number;
  complete?: boolean;
  pdfUrl?: string;
  canRead?: boolean;
  onProgress?: (progress: { accumulated: number; complete: boolean; testUnlocked: boolean }) => void;
}

export default function PdfReader({
  enrollmentId,
  sectionOrder = 1,
  title = "Sección",
  content = "",
  minimumSeconds,
  sectionBaseSeconds = 0,
  accumulatedSeconds = 0,
  complete: initialComplete = false,
  pdfUrl,
  canRead = true,
  onProgress,
}: PdfReaderProps) {
  const [accumulated, setAccumulated] = useState(accumulatedSeconds);
  const [complete, setComplete] = useState(initialComplete);
  const [locked, setLocked] = useState(false);
  const [error, setError] = useState("");
  const [numPages, setNumPages] = useState(0);
  const [pageNumber, setPageNumber] = useState(1);
  const lastInteraction = useRef(Date.now());
  const onProgressRef = useRef(onProgress);

  useEffect(() => { onProgressRef.current = onProgress; }, [onProgress]);

  useEffect(() => {
    setAccumulated(accumulatedSeconds);
    setComplete(initialComplete);
    setLocked(false);
    setError("");
    setPageNumber(1);
  }, [sectionOrder, accumulatedSeconds, initialComplete]);

  useEffect(() => {
    const markInteraction = () => { lastInteraction.current = Date.now(); };
    const events: Array<keyof WindowEventMap> = ["pointerdown", "keydown", "scroll", "touchstart"];
    events.forEach((event) => window.addEventListener(event, markInteraction, { passive: true }));
    return () => events.forEach((event) => window.removeEventListener(event, markInteraction));
  }, []);

  useEffect(() => {
    if (!canRead || complete) return;
    const interval = window.setInterval(async () => {
      try {
        const response = await client.post("/reading/heartbeat", {
          enrollment_id: enrollmentId,
          section_order: sectionOrder,
          delta: 5,
          visibility: document.visibilityState === "visible",
          interaction: Date.now() - lastInteraction.current < 30_000,
        });
        setLocked(Boolean(response.data.locked));
        if (typeof response.data.accumulated === "number") {
          setAccumulated(response.data.accumulated);
        }
        const sectionComplete = Boolean(response.data.section_complete);
        setComplete(sectionComplete);
        onProgressRef.current?.({
          accumulated: response.data.accumulated || 0,
          complete: sectionComplete,
          testUnlocked: Boolean(response.data.test_unlocked),
        });
      } catch (requestError: any) {
        setError(requestError?.response?.data?.error || "Error de conexión con el servidor");
      }
    }, 5000);
    return () => window.clearInterval(interval);
  }, [canRead, complete, enrollmentId, sectionOrder]);

  const requiredSeconds = minimumSeconds ?? Math.ceil(sectionBaseSeconds / 3);
  const remaining = Math.max(0, requiredSeconds - accumulated);
  const width = Math.min(760, window.innerWidth - 48);

  return (
    <div data-testid="pdf-reader">
      <Card>
        <h2 style={{ marginBottom: "var(--space-sm)" }}>{title}</h2>
        <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.65 }}>{content}</div>
      </Card>

      {pdfUrl && (
        <Card style={{ marginTop: "var(--space-md)", overflowX: "auto" }}>
          <Document
            file={{ url: pdfUrl }}
            options={{ withCredentials: true }}
            onLoadSuccess={({ numPages: pages }) => setNumPages(pages)}
            onLoadError={() => setError("Error al cargar el PDF")}
          >
            <Page pageNumber={pageNumber} width={width} />
          </Document>
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 12, marginTop: 8 }}>
            <Button variant="secondary" size="sm" onClick={() => setPageNumber((page) => Math.max(1, page - 1))} disabled={pageNumber <= 1}>Anterior</Button>
            <span>Página {pageNumber} de {numPages || "..."}</span>
            <Button variant="secondary" size="sm" onClick={() => setPageNumber((page) => Math.min(numPages, page + 1))} disabled={pageNumber >= numPages}>Siguiente</Button>
          </div>
        </Card>
      )}

      <div role="status" style={{ marginTop: 12, padding: 12, borderRadius: 6, background: complete ? "var(--color-success-bg)" : "var(--color-warning-bg)" }}>
        {!canRead && "Curso pausado o cancelado. El contador está detenido."}
        {canRead && locked && "Completa la sección anterior para continuar."}
        {canRead && !locked && !complete && `Tiempo activo: ${accumulated}s. Restan ${remaining}s.`}
        {canRead && complete && `Sección completada. Tiempo activo: ${accumulated}s.`}
      </div>
      {error && <p role="alert" style={{ color: "var(--color-danger)", marginTop: 8 }}>{error}</p>}
    </div>
  );
}

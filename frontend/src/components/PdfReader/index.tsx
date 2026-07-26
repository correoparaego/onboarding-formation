import { useEffect, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import client from "../../api/client";
import { Button } from "../ui";

import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export interface PdfReaderProps {
  enrollmentId: number;
  sectionId: number;
  sectionBaseSeconds: number;
  minTimeDivisor?: number;
  pdfUrl: string;
}

export default function PdfReader({
  enrollmentId,
  sectionId,
  sectionBaseSeconds,
  minTimeDivisor = 3,
  pdfUrl,
}: PdfReaderProps) {
  const [locked, setLocked] = useState(true);
  const [remaining, setRemaining] = useState(Math.ceil(sectionBaseSeconds / minTimeDivisor));
  const [error, setError] = useState("");
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState(1);
  const heartbeatRef = useRef<number | null>(null);

  useEffect(() => {
    const interval = 5000;
    heartbeatRef.current = window.setInterval(() => {
      const delta = interval / 1000;
      client
        .post("/reading/heartbeat", {
          enrollment_id: enrollmentId,
          section_id: sectionId,
          delta,
          visible: document.visibilityState === "visible",
        })
        .then((r) => {
          if (r.data.unlocked) {
            setLocked(false);
          }
          const serverRemaining = r.data.remaining_seconds;
          if (typeof serverRemaining === "number") {
            setRemaining(Math.ceil(serverRemaining));
          }
        })
        .catch((e) => {
          setError(e?.response?.data?.error || "Error de conexión con el servidor");
        });
    }, interval);
    return () => {
      if (heartbeatRef.current) window.clearInterval(heartbeatRef.current);
    };
  }, [enrollmentId, sectionId]);

  if (!pdfUrl) {
    return (
      <div data-testid="pdf-reader" style={{ padding: "var(--space-lg)", textAlign: "center" }}>
        <p style={{ color: "var(--color-text-muted)" }}>No hay PDF disponible para este curso.</p>
      </div>
    );
  }

  return (
    <div data-testid="pdf-reader" style={{ padding: "var(--space-md)" }}>
      <div data-testid="pdf-viewer">
        <Document
          file={pdfUrl}
          onLoadSuccess={({ numPages }) => setNumPages(numPages)}
          onLoadError={() => setError("Error al cargar el PDF")}
        >
          <Page pageNumber={pageNumber} width={800} />
        </Document>
      </div>
      <div
        style={{
          marginTop: "var(--space-sm)",
          display: "flex",
          gap: "var(--space-sm)",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Button
          data-testid="section-nav-btn"
          variant="secondary"
          size="sm"
          onClick={() => setPageNumber((p) => Math.max(1, p - 1))}
          disabled={pageNumber <= 1}
          aria-label="Página anterior"
        >
          Anterior
        </Button>
        <span data-testid="reading-timer" aria-live="polite" style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
          Página {pageNumber} de {numPages || "..."}
        </span>
        <Button
          data-testid="section-nav-btn"
          variant="secondary"
          size="sm"
          onClick={() => setPageNumber((p) => Math.min(numPages, p + 1))}
          disabled={pageNumber >= numPages}
          aria-label="Página siguiente"
        >
          Siguiente
        </Button>
      </div>
      {locked && (
        <p
          data-testid="locked-overlay"
          role="status"
          aria-live="polite"
          style={{
            marginTop: "var(--space-md)",
            padding: "var(--space-sm) var(--space-md)",
            background: "var(--color-warning-bg)",
            color: "var(--color-warning-text)",
            borderRadius: "var(--radius-sm)",
            fontSize: "var(--font-size-sm)",
            textAlign: "center",
          }}
        >
          Sección bloqueada — tiempo restante: {remaining}s
        </p>
      )}
      {!locked && (
        <p
          data-testid="unlocked-message"
          role="status"
          aria-live="polite"
          style={{
            marginTop: "var(--space-md)",
            padding: "var(--space-sm) var(--space-md)",
            background: "var(--color-success-bg)",
            color: "var(--color-success-text)",
            borderRadius: "var(--radius-sm)",
            fontSize: "var(--font-size-sm)",
            textAlign: "center",
          }}
        >
          Sección desbloqueada — puedes acceder al test
        </p>
      )}
      {error && (
        <p
          role="alert"
          aria-live="assertive"
          style={{ color: "var(--color-danger)", marginTop: "var(--space-sm)", fontSize: "var(--font-size-sm)" }}
        >
          {error}
        </p>
      )}
    </div>
  );
}

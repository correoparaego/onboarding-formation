import { useEffect, useRef, useState } from "react";
import client from "../../api/client";

export interface PdfReaderProps {
  enrollmentId: number;
  sectionId: number;
  // Total estimated base seconds for this section (section_base).
  sectionBaseSeconds: number;
  // min_time_divisor from the course (default 3).
  minTimeDivisor?: number;
  pdfUrl: string;
}

/**
 * Section-gated PDF reader (scaffold).
 *
 * PR1 only establishes the component shell and the heartbeat shape. The actual
 * server-authoritative gating logic (visibility/interaction validation, unlock
 * at section_base / divisor) is implemented in Phase 9 (timed-reading gate).
 */
export default function PdfReader({
  enrollmentId,
  sectionId,
  sectionBaseSeconds,
  minTimeDivisor = 3,
  pdfUrl,
}: PdfReaderProps) {
  const [locked] = useState(true);
  const [remaining] = useState(Math.ceil(sectionBaseSeconds / minTimeDivisor));
  const heartbeatRef = useRef<number | null>(null);

  useEffect(() => {
    // Placeholder heartbeat loop — real gating lands in Phase 9.
    heartbeatRef.current = window.setInterval(() => {
      client
        .post("/reading/heartbeat", {
          enrollment_id: enrollmentId,
          section_id: sectionId,
          delta: 1,
          visible: document.visibilityState === "visible",
        })
        .catch(() => {
          /* no-op in scaffold */
        });
    }, 1000);
    return () => {
      if (heartbeatRef.current) window.clearInterval(heartbeatRef.current);
    };
  }, [enrollmentId, sectionId]);

  return (
    <div data-testid="pdf-reader">
      <iframe title="course-pdf" src={pdfUrl} style={{ width: "100%", height: 600 }} />
      {locked && (
        <p>
          Sección bloqueada — restante: {remaining}s (placeholder; gating en fase 9)
        </p>
      )}
    </div>
  );
}

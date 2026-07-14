import { Routes, Route } from "react-router-dom";
import PdfReader from "../components/PdfReader";

// Employee shell — token-gated reader, test, badges.
// Phase 1 scaffold only; auth/token gating lands in Phase 3.
export default function EmployeeApp() {
  return (
    <div>
      <h1>Portal del empleado</h1>
      <Routes>
        <Route
          path="read"
          element={
            <PdfReader
              enrollmentId={0}
              sectionId={0}
              sectionBaseSeconds={0}
              pdfUrl=""
            />
          }
        />
        <Route path="*" element={<p>Introduce tu código de acceso (fase 3).</p>} />
      </Routes>
    </div>
  );
}

import { Routes, Route, Link } from "react-router-dom";

import AiKeyForm from "./ai/AiKeyForm";
import GuidedContent from "./ai/GuidedContent";
import PdfTestGen from "./ai/PdfTestGen";

// Admin shell — import, course CRUD, catalog, expediente, AI authoring live here.
export default function AdminApp() {
  return (
    <div>
      <h1>Administración</h1>
      <nav>
        <Link to="/admin/import">Importar empleados</Link> ·{" "}
        <Link to="/admin/courses">Cursos</Link> ·{" "}
        <Link to="/admin/ai/key">IA: clave</Link> ·{" "}
        <Link to="/admin/ai/content">IA: contenido</Link> ·{" "}
        <Link to="/admin/ai/tests">IA: test PDF</Link> ·{" "}
        <Link to="/admin/expediente">Expediente</Link>
      </nav>
      <Routes>
        <Route path="import" element={<p>Importación (fase 4)</p>} />
        <Route path="courses" element={<p>Cursos (fase 5)</p>} />
        <Route path="ai/key" element={<AiKeyForm />} />
        <Route path="ai/content" element={<GuidedContent />} />
        <Route path="ai/tests" element={<PdfTestGen />} />
        <Route path="expediente" element={<p>Expediente (fase 13)</p>} />
        <Route path="*" element={<p>Selecciona una sección.</p>} />
      </Routes>
    </div>
  );
}

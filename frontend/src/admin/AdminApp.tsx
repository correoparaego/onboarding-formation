import { Routes, Route, Link } from "react-router-dom";

// Admin shell — import, course CRUD, catalog, expediente, AI authoring live here.
// Phase 1 scaffold only; screens are filled in by later phases.
export default function AdminApp() {
  return (
    <div>
      <h1>Administración</h1>
      <nav>
        <Link to="/admin/import">Importar empleados</Link> ·{" "}
        <Link to="/admin/courses">Cursos</Link> ·{" "}
        <Link to="/admin/expediente">Expediente</Link>
      </nav>
      <Routes>
        <Route path="import" element={<p>Importación (fase 4)</p>} />
        <Route path="courses" element={<p>Cursos (fase 5)</p>} />
        <Route path="expediente" element={<p>Expediente (fase 13)</p>} />
        <Route path="*" element={<p>Selecciona una sección.</p>} />
      </Routes>
    </div>
  );
}

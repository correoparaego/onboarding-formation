import { Routes, Route } from "react-router-dom";
import AdminApp from "./admin/AdminApp";
import EmployeeApp from "./employee/EmployeeApp";

// Top-level router. Auth gating and route isolation are implemented in Phase 3.
export default function App() {
  return (
    <Routes>
      <Route path="/admin/*" element={<AdminApp />} />
      <Route path="/employee/*" element={<EmployeeApp />} />
      <Route
        path="*"
        element={
          <div>
            <h1>Formación Inicial</h1>
            <p>
              <a href="/admin">Acceso administración</a> ·{" "}
              <a href="/employee">Acceso empleado</a>
            </p>
          </div>
        }
      />
    </Routes>
  );
}

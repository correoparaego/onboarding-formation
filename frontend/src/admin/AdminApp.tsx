import { lazy, Suspense } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import ProtectedRoute from "../auth/ProtectedRoute";
import EmployeeImport from "./EmployeeImport";
import CourseManagement from "./CourseManagement";
import ExpedienteList from "./ExpedienteList";
import Dashboard from "./Dashboard";
import AdminLayout from "../components/layout/AdminLayout";
import { SkeletonCard } from "../components/ui";

const AiKeyForm = lazy(() => import("./ai/AiKeyForm"));
const GuidedContent = lazy(() => import("./ai/GuidedContent"));
const PdfTestGen = lazy(() => import("./ai/PdfTestGen"));

export default function AdminApp() {
  const { admin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/admin/login");
  };

  return (
    <ProtectedRoute role="admin">
      <div data-testid="admin-app-container">
      <AdminLayout adminName={admin?.username} onLogout={handleLogout}>
        <Routes>
          <Route index element={<Dashboard />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="import" element={<EmployeeImport />} />
          <Route path="courses" element={<CourseManagement />} />
          <Route
            path="ai/key"
            element={
              <Suspense fallback={<SkeletonCard count={1} />}>
                <AiKeyForm />
              </Suspense>
            }
          />
          <Route
            path="ai/content"
            element={
              <Suspense fallback={<SkeletonCard count={1} />}>
                <GuidedContent />
              </Suspense>
            }
          />
          <Route
            path="ai/tests"
            element={
              <Suspense fallback={<SkeletonCard count={1} />}>
                <PdfTestGen />
              </Suspense>
            }
          />
          <Route path="expediente" element={<ExpedienteList />} />
          <Route path="*" element={<p style={{ color: "var(--color-text-muted)" }}>Selecciona una sección.</p>} />
        </Routes>
      </AdminLayout>
      </div>
    </ProtectedRoute>
  );
}

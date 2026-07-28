import { useEffect, useState } from "react";

import {
  accessCodesApi,
  AdminEnrollment,
  assignmentsApi,
  coursesApi,
  EmployeeSummary,
  EmployeeAccessCodeResult,
  employeesApi,
} from "../api/endpoints";
import Breadcrumb from "../components/layout/Breadcrumb";
import { Badge, Button, Card, ConfirmDialog } from "../components/ui";
import { useToast } from "../contexts/ToastContext";

interface Preview {
  employees: Array<{ id: number; name: string; position: string }>;
  courses: Array<{ id: number; title: string }>;
  new_assignments: number;
  existing_assignments: number;
}

const toggle = (values: number[], id: number) =>
  values.includes(id) ? values.filter((value) => value !== id) : [...values, id];

export default function AssignmentManagement() {
  const [employees, setEmployees] = useState<EmployeeSummary[]>([]);
  const [positions, setPositions] = useState<Array<{ id: number; name: string }>>([]);
  const [courses, setCourses] = useState<Array<{ id: number; title: string }>>([]);
  const [enrollments, setEnrollments] = useState<AdminEnrollment[]>([]);
  const [employeeIds, setEmployeeIds] = useState<number[]>([]);
  const [positionIds, setPositionIds] = useState<number[]>([]);
  const [courseIds, setCourseIds] = useState<number[]>([]);
  const [excludedIds, setExcludedIds] = useState<number[]>([]);
  const [bulkPositionId, setBulkPositionId] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [accessResults, setAccessResults] = useState<EmployeeAccessCodeResult[]>([]);
  const [showAccessConfirm, setShowAccessConfirm] = useState(false);
  const [generatingAccess, setGeneratingAccess] = useState(false);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  const load = async () => {
    setLoading(true);
    try {
      const [employeeResponse, positionResponse, courseResponse, enrollmentResponse] = await Promise.all([
        employeesApi.list(),
        coursesApi.positions(),
        coursesApi.list(),
        assignmentsApi.enrollments(),
      ]);
      setEmployees(employeeResponse.data.results);
      setPositions(positionResponse.data.positions);
      setCourses(courseResponse.data.courses);
      setEnrollments(enrollmentResponse.data.enrollments);
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "Error al cargar asignaciones");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const selection = () => ({
    course_ids: courseIds,
    employee_ids: employeeIds,
    position_ids: positionIds,
    exclude_ids: excludedIds,
  });

  const previewAssignment = async () => {
    if (!courseIds.length || (!employeeIds.length && !positionIds.length)) {
      toast.error("Selecciona cursos y empleados o puestos");
      return;
    }
    try {
      const response = await assignmentsApi.preview(selection());
      setPreview(response.data);
      setExcludedIds([]);
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "No se pudo calcular la asignación");
    }
  };

  const applyAssignment = async () => {
    try {
      const response = await assignmentsApi.apply(selection());
      toast.success(`${response.data.created} matrículas creadas`);
      setPreview(null);
      setEmployeeIds([]);
      setPositionIds([]);
      setCourseIds([]);
      setExcludedIds([]);
      load();
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "Error al asignar cursos");
    }
  };

  const changePositions = async () => {
    if (!employeeIds.length || !bulkPositionId) return;
    try {
      await employeesApi.bulkPosition(employeeIds, Number(bulkPositionId));
      toast.success("Puestos actualizados sin modificar el histórico");
      setEmployeeIds([]);
      setBulkPositionId("");
      load();
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "Error al cambiar puestos");
    }
  };

  const runAction = async (enrollment: AdminEnrollment, action: "pause" | "resume" | "cancel" | "repeat") => {
    try {
      await assignmentsApi.action(enrollment.id, action);
      toast.success("Estado actualizado");
      load();
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "Transición no permitida");
    }
  };

  const generateAccessCodes = async (ids = employeeIds) => {
    if (!ids.length) return;
    setGeneratingAccess(true);
    try {
      const response = await accessCodesApi.generateBatch(ids);
      setAccessResults((current) => {
        const replacedIds = new Set(response.data.results.map((result) => result.employee_id));
        return [
          ...current.filter((result) => !replacedIds.has(result.employee_id)),
          ...response.data.results,
        ];
      });
      setShowAccessConfirm(false);
      if (response.data.missing_employee_ids.length || response.data.errors.length) {
        toast.error(`${response.data.results.length} códigos generados; algunas personas no se procesaron`);
      } else {
        toast.success(`${response.data.results.length} códigos generados`);
      }
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "No se pudieron generar los accesos");
    } finally {
      setGeneratingAccess(false);
    }
  };

  const copyAllCodes = async () => {
    await navigator.clipboard.writeText(
      accessResults.map((result) => `${result.employee_name}: ${result.code}`).join("\n")
    );
    toast.success("Códigos copiados");
  };

  if (loading) return <p style={{ color: "var(--color-text-muted)" }}>Cargando gestión...</p>;

  return (
    <div>
      <Breadcrumb items={[{ label: "Inicio", to: "/admin/dashboard" }, { label: "Asignaciones" }]} />
      <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-lg)" }}>Empleados y asignaciones</h2>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "var(--space-md)" }}>
        <Card>
          <h3>1. Empleados individuales</h3>
          <div style={{ maxHeight: 240, overflowY: "auto", marginTop: "var(--space-sm)" }}>
            {employees.map((employee) => (
              <label key={employee.id} style={{ display: "flex", gap: 8, padding: 6 }}>
                <input type="checkbox" checked={employeeIds.includes(employee.id)} onChange={() => setEmployeeIds(toggle(employeeIds, employee.id))} />
                <span>{employee.name} <small>({employee.current_position?.name || employee.position})</small></span>
              </label>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: "var(--space-md)" }}>
            <select value={bulkPositionId} onChange={(event) => setBulkPositionId(event.target.value)} style={{ flex: 1 }}>
              <option value="">Cambiar puesto a...</option>
              {positions.map((position) => <option key={position.id} value={position.id}>{position.name}</option>)}
            </select>
            <Button size="sm" onClick={changePositions} disabled={!employeeIds.length || !bulkPositionId}>Aplicar</Button>
          </div>
          <Button
            onClick={() => setShowAccessConfirm(true)}
            disabled={!employeeIds.length || generatingAccess}
            style={{ width: "100%", marginTop: "var(--space-sm)" }}
          >
            {generatingAccess ? "Generando..." : "Generar y enviar accesos"}
          </Button>
        </Card>

        <Card>
          <h3>2. Grupos por puesto</h3>
          <div style={{ marginTop: "var(--space-sm)" }}>
            {positions.map((position) => (
              <label key={position.id} style={{ display: "flex", gap: 8, padding: 6 }}>
                <input type="checkbox" checked={positionIds.includes(position.id)} onChange={() => setPositionIds(toggle(positionIds, position.id))} />
                {position.name}
              </label>
            ))}
          </div>
        </Card>

        <Card>
          <h3>3. Cursos</h3>
          <div style={{ marginTop: "var(--space-sm)" }}>
            {courses.map((course) => (
              <label key={course.id} style={{ display: "flex", gap: 8, padding: 6 }}>
                <input type="checkbox" checked={courseIds.includes(course.id)} onChange={() => setCourseIds(toggle(courseIds, course.id))} />
                {course.title}
              </label>
            ))}
          </div>
          <Button onClick={previewAssignment} style={{ marginTop: "var(--space-md)" }}>Revisar asignación</Button>
        </Card>
      </div>

      {preview && (
        <Card style={{ marginTop: "var(--space-lg)" }}>
          <h3>Vista previa</h3>
          <p>{preview.new_assignments} nuevas; {preview.existing_assignments} ya existentes.</p>
          <p style={{ color: "var(--color-text-secondary)" }}>Desmarca personas para excluirlas de esta operación.</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, margin: "var(--space-md) 0" }}>
            {preview.employees.map((employee) => (
              <label key={employee.id} style={{ border: "1px solid var(--color-border)", borderRadius: 6, padding: 8 }}>
                <input type="checkbox" checked={!excludedIds.includes(employee.id)} onChange={() => setExcludedIds(toggle(excludedIds, employee.id))} /> {employee.name}
              </label>
            ))}
          </div>
          <Button onClick={applyAssignment}>Confirmar asignación</Button>
        </Card>
      )}

      {accessResults.length > 0 && (
        <Card style={{ marginTop: "var(--space-lg)", overflowX: "auto" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
            <div>
              <h3>Códigos generados</h3>
              <p style={{ color: "var(--color-text-secondary)" }}>Se muestran una sola vez. Un reintento invalida el código anterior.</p>
            </div>
            <Button size="sm" variant="secondary" onClick={copyAllCodes}>Copiar todos</Button>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "var(--space-md)" }}>
            <thead><tr><th>Empleado</th><th>Correo</th><th>Código</th><th>Envío</th><th>Caduca</th><th>Acciones</th></tr></thead>
            <tbody>
              {accessResults.map((result) => (
                <tr key={result.employee_id}>
                  <td>{result.employee_name}</td>
                  <td>{result.email || "Sin correo"}</td>
                  <td><code style={{ fontSize: "var(--font-size-lg)", letterSpacing: 1 }}>{result.code}</code></td>
                  <td><Badge variant={result.delivery_status === "sent" ? "success" : result.delivery_status === "failed" ? "danger" : "warning"}>{result.delivery_status}</Badge></td>
                  <td>{new Date(result.expires_at).toLocaleString()}</td>
                  <td style={{ display: "flex", gap: 4 }}>
                    <Button size="sm" variant="ghost" onClick={() => navigator.clipboard.writeText(result.code)}>Copiar</Button>
                    {result.delivery_status !== "sent" && <Button size="sm" variant="ghost" disabled={generatingAccess} onClick={() => generateAccessCodes([result.employee_id])}>Reintentar</Button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      <Card style={{ marginTop: "var(--space-lg)", overflowX: "auto" }}>
        <h3 style={{ marginBottom: "var(--space-md)" }}>Realizaciones e histórico</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead><tr><th>Empleado</th><th>Curso</th><th>Ciclo</th><th>Estado</th><th>Tiempo activo</th><th>Acciones</th></tr></thead>
          <tbody>
            {enrollments.map((enrollment) => (
              <tr key={enrollment.id}>
                <td>{enrollment.employee_name}</td><td>{enrollment.course_title} v{enrollment.version || "-"}</td><td>{enrollment.cycle}</td>
                <td><Badge>{enrollment.status}</Badge></td><td>{Math.floor(enrollment.active_seconds / 60)}m {enrollment.active_seconds % 60}s</td>
                <td style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {["assigned", "in_progress"].includes(enrollment.status) && <Button size="sm" variant="ghost" onClick={() => runAction(enrollment, "pause")}>Pausar</Button>}
                  {enrollment.status === "paused" && <Button size="sm" variant="ghost" onClick={() => runAction(enrollment, "resume")}>Reanudar</Button>}
                  {["assigned", "in_progress", "paused", "complete"].includes(enrollment.status) && <Button size="sm" variant="ghost" onClick={() => runAction(enrollment, "cancel")}>Cancelar</Button>}
                  {["cancelled", "passed", "failed_exhausted"].includes(enrollment.status) && <Button size="sm" variant="ghost" onClick={() => runAction(enrollment, "repeat")}>Repetir</Button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
      <ConfirmDialog
        isOpen={showAccessConfirm}
        onConfirm={() => generateAccessCodes()}
        onCancel={() => setShowAccessConfirm(false)}
        title="Generar nuevos accesos"
        message={`Se invalidarán los códigos anteriores de ${employeeIds.length} empleados y se intentará enviar un correo individual a cada uno.`}
        confirmLabel="Generar y enviar"
      />
    </div>
  );
}

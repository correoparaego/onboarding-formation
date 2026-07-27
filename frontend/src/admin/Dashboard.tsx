import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import client from "../api/client";
import { Card } from "../components/ui";
import { useTheme } from "../contexts/ThemeContext";
import Breadcrumb from "../components/layout/Breadcrumb";

interface EmployeeRow {
  id: number;
  name: string;
  position: string;
  email: string;
  phone: string;
}

interface EmployeeResponse {
  count: number;
  results: EmployeeRow[];
}

interface ExpedienteRow {
  employee_id: number;
  employee_name: string;
  course_id: number;
  course_title: string;
  status: string;
  score: number | null;
  total: number | null;
}

interface ExpedienteResponse {
  count: number;
  results: ExpedienteRow[];
}

interface CourseStats {
  course: string;
  passRate: number;
}

interface StatusStats {
  name: string;
  value: number;
}

const STATUS_LABELS: Record<string, string> = {
  pending: "Pendiente",
  in_progress: "En progreso",
  completed: "Completado",
  failed: "Fallido",
};

export default function Dashboard() {
  const { isDark } = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [totalEmployees, setTotalEmployees] = useState(0);
  const [totalCourses, setTotalCourses] = useState(0);
  const [completionRate, setCompletionRate] = useState(0);
  const [courseStats, setCourseStats] = useState<CourseStats[]>([]);
  const [statusStats, setStatusStats] = useState<StatusStats[]>([]);

  const chartColors = {
    primary: isDark ? "#4dabf7" : "#007bff",
    success: isDark ? "#51cf66" : "#28a745",
    warning: isDark ? "#ffd43b" : "#ffc107",
    danger: isDark ? "#ff6b6b" : "#dc3545",
    text: isDark ? "#e4e6eb" : "#212529",
    textSecondary: isDark ? "#b0b3b8" : "#6c757d",
    grid: isDark ? "#3a3b3c" : "#dee2e6",
    bg: isDark ? "#1a1a2e" : "#ffffff",
  };

  const PIE_COLORS = [chartColors.primary, chartColors.warning, chartColors.success, chartColors.danger];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      // Fetch employee count from /api/employees (source of truth for total employees)
      const empResponse = await client.get<EmployeeResponse>("/employees", { params: { limit: 1, offset: 0 } });
      setTotalEmployees(empResponse.data.count);

      // Fetch expediente data for course statistics
      const r = await client.get<ExpedienteResponse>("/expediente", { params: { limit: 1000, offset: 0 } });
      const data = r.data.results;

      const uniqueCourses = new Set(data.map((d) => d.course_id));
      setTotalCourses(uniqueCourses.size);

      const completed = data.filter((d) => d.status === "completed").length;
      setCompletionRate(data.length > 0 ? Math.round((completed / data.length) * 100) : 0);

      const courseMap = new Map<string, { total: number; passed: number }>();
      data.forEach((d) => {
        const entry = courseMap.get(d.course_title) || { total: 0, passed: 0 };
        entry.total++;
        if (d.status === "completed") entry.passed++;
        courseMap.set(d.course_title, entry);
      });
      const cStats: CourseStats[] = [];
      courseMap.forEach((v, k) => {
        cStats.push({ course: k, passRate: Math.round((v.passed / v.total) * 100) });
      });
      setCourseStats(cStats);

      const statusMap = new Map<string, number>();
      data.forEach((d) => {
        statusMap.set(d.status, (statusMap.get(d.status) || 0) + 1);
      });
      const sStats: StatusStats[] = [];
      statusMap.forEach((v, k) => {
        sStats.push({ name: STATUS_LABELS[k] || k, value: v });
      });
      setStatusStats(sStats);
    } catch (e: any) {
      setError(e?.response?.data?.error || "Error al cargar datos del dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <p style={{ color: "var(--color-text-muted)" }}>Cargando dashboard...</p>;
  }

  return (
    <div>
      <Breadcrumb items={[{ label: "Inicio", to: "/admin/dashboard" }, { label: "Dashboard" }]} />
      <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-lg)" }}>Dashboard</h2>

      {error && (
        <p role="alert" style={{ color: "var(--color-danger)", marginBottom: "var(--space-md)" }}>
          {error}
        </p>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "var(--space-md)",
          marginBottom: "var(--space-lg)",
        }}
      >
        <Card style={{ textAlign: "center" }}>
          <div style={{ fontSize: "var(--font-size-3xl)", fontWeight: 700, color: "var(--color-primary)" }}>
            {totalEmployees}
          </div>
          <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)" }}>Empleados</div>
        </Card>
        <Card style={{ textAlign: "center" }}>
          <div style={{ fontSize: "var(--font-size-3xl)", fontWeight: 700, color: "var(--color-primary)" }}>
            {totalCourses}
          </div>
          <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)" }}>Cursos</div>
        </Card>
        <Card style={{ textAlign: "center" }}>
          <div style={{ fontSize: "var(--font-size-3xl)", fontWeight: 700, color: "var(--color-success)" }}>
            {completionRate}%
          </div>
          <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)" }}>Tasa completado</div>
        </Card>
        <Card style={{ textAlign: "center" }}>
          <div style={{ fontSize: "var(--font-size-3xl)", fontWeight: 700, color: "var(--color-info)" }}>
            {statusStats.find((s) => s.name === "En progreso")?.value || 0}
          </div>
          <div style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)" }}>Activos</div>
        </Card>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: "var(--space-lg)" }}>
        <Card>
          <h3 style={{ marginBottom: "var(--space-md)", fontSize: "var(--font-size-lg)" }}>
            Tasa de aprobados por curso
          </h3>
          {courseStats.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={courseStats} margin={{ top: 5, right: 20, left: 0, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis
                  dataKey="course"
                  tick={{ fontSize: 11, fill: chartColors.textSecondary }}
                  angle={-30}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12, fill: chartColors.textSecondary }} unit="%" />
                <Tooltip
                  contentStyle={{
                    background: chartColors.bg,
                    border: `1px solid ${chartColors.grid}`,
                    borderRadius: 4,
                    color: chartColors.text,
                  }}
                />
                <Bar dataKey="passRate" fill={chartColors.primary} radius={[4, 4, 0, 0]} name="Aprobados %" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: "var(--color-text-muted)", textAlign: "center", padding: "var(--space-lg)" }}>
              Sin datos de cursos
            </p>
          )}
        </Card>

        <Card>
          <h3 style={{ marginBottom: "var(--space-md)", fontSize: "var(--font-size-lg)" }}>
            Distribución por estado
          </h3>
          {statusStats.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusStats}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                >
                  {statusStats.map((_, index) => (
                    <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: chartColors.bg,
                    border: `1px solid ${chartColors.grid}`,
                    borderRadius: 4,
                    color: chartColors.text,
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: "var(--color-text-muted)", textAlign: "center", padding: "var(--space-lg)" }}>
              Sin datos de estado
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}

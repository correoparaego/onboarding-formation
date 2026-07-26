import { useEffect, useState, useMemo } from "react";
import client from "../api/client";
import { Button, Badge, Input, EmptyState, SkeletonTable, ResponsiveTable } from "../components/ui";
import Breadcrumb from "../components/layout/Breadcrumb";

interface Expediente {
  employee_id: number;
  employee_name: string;
  dni: string;
  course_id: number;
  course_title: string;
  status: string;
  attempts_used: number;
  score: number | null;
  total: number | null;
  completed_at: string | null;
}

interface ExpedienteResponse {
  count: number;
  limit: number;
  offset: number;
  results: Expediente[];
}

const getStatusVariant = (status: string): "success" | "warning" | "danger" | "info" | "neutral" => {
  switch (status) {
    case "completed": return "success";
    case "in_progress": return "warning";
    case "pending": return "neutral";
    case "failed": return "danger";
    default: return "neutral";
  }
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case "completed": return "Completado";
    case "in_progress": return "En progreso";
    case "pending": return "Pendiente";
    case "failed": return "Fallido";
    default: return status;
  }
};

const columns = [
  { key: "employee_name", label: "Empleado" },
  { key: "dni", label: "DNI" },
  { key: "course_title", label: "Curso" },
  {
    key: "status",
    label: "Estado",
    render: (row: Expediente) => (
      <Badge variant={getStatusVariant(row.status)} size="sm">
        {getStatusLabel(row.status)}
      </Badge>
    ),
  },
  { key: "attempts_used", label: "Intentos" },
  {
    key: "score",
    label: "Puntuación",
    render: (row: Expediente) =>
      row.score !== null && row.total !== null ? `${row.score}/${row.total}` : "-",
  },
  {
    key: "completed_at",
    label: "Completado",
    render: (row: Expediente) =>
      row.completed_at ? new Date(row.completed_at).toLocaleString("es-ES") : "-",
  },
];

export default function ExpedienteList() {
  const [expedientes, setExpedientes] = useState<Expediente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [total, setTotal] = useState(0);
  const [limit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [courseFilter, setCourseFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadExpedientes();
  }, [offset, courseFilter, statusFilter]);

  const loadExpedientes = async () => {
    setLoading(true);
    setError("");
    try {
      const params: any = { limit, offset };
      if (courseFilter) params.course = courseFilter;
      if (statusFilter) params.status = statusFilter;
      const r = await client.get<ExpedienteResponse>("/expediente", { params });
      setExpedientes(r.data.results);
      setTotal(r.data.count);
    } catch (e: any) {
      setError(e?.response?.data?.error || "Error al cargar expedientes");
    } finally {
      setLoading(false);
    }
  };

  const filteredExpedientes = useMemo(() => {
    if (!search.trim()) return expedientes;
    const q = search.toLowerCase();
    return expedientes.filter(
      (e) =>
        e.employee_name.toLowerCase().includes(q) ||
        e.course_title.toLowerCase().includes(q) ||
        e.dni.toLowerCase().includes(q)
    );
  }, [expedientes, search]);

  const resetFilters = () => {
    setCourseFilter("");
    setStatusFilter("");
    setSearch("");
    setOffset(0);
  };

  const nextPage = () => {
    if (offset + limit < total) {
      setOffset(offset + limit);
    }
  };

  const prevPage = () => {
    if (offset > 0) {
      setOffset(Math.max(0, offset - limit));
    }
  };

  return (
    <div data-testid="expediente-page">
      <Breadcrumb items={[{ label: "Inicio", to: "/admin/dashboard" }, { label: "Expediente" }]} />
      <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-md)" }}>Expediente de empleados</h2>

      <div
        style={{
          display: "flex",
          gap: "var(--space-md)",
          marginBottom: "var(--space-md)",
          padding: "var(--space-md)",
          background: "var(--color-bg-secondary)",
          borderRadius: "var(--radius-md)",
          flexWrap: "wrap",
          alignItems: "flex-end",
        }}
      >
        <div style={{ flex: "1 1 200px" }}>
          <Input
            data-testid="expediente-search-input"
            label="Buscar"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Nombre, curso o DNI..."
            icon="🔍"
          />
        </div>
        <div>
          <Input
            label="Curso"
            value={courseFilter}
            onChange={(e) => { setCourseFilter(e.target.value); setOffset(0); }}
            placeholder="ID o título"
            style={{ width: 200 }}
          />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "var(--font-size-sm)", marginBottom: "var(--space-xs)", fontWeight: 500 }}>
            Estado
          </label>
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setOffset(0); }}
            style={{ width: 150 }}
          >
            <option value="">Todos</option>
            <option value="pending">Pendiente</option>
            <option value="in_progress">En progreso</option>
            <option value="completed">Completado</option>
            <option value="failed">Fallido</option>
          </select>
        </div>
        <Button variant="secondary" size="sm" onClick={resetFilters}>
          Limpiar filtros
        </Button>
      </div>

      {error && (
        <p role="alert" aria-live="assertive" style={{ color: "var(--color-danger)", marginBottom: "var(--space-md)" }}>
          {error}
        </p>
      )}

      {loading ? (
        <SkeletonTable rows={5} cols={6} />
      ) : filteredExpedientes.length === 0 ? (
        <EmptyState
          icon="📋"
          title="No hay expedientes"
          description={
            search
              ? "No se encontraron resultados para tu búsqueda."
              : "No hay expedientes que coincidan con los filtros seleccionados."
          }
        />
      ) : (
        <>
          <div style={{ marginBottom: "var(--space-sm)", fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
            Mostrando {offset + 1}-{Math.min(offset + limit, total)} de {total} expedientes
            {search && ` (${filteredExpedientes.length} filtrados)`}
          </div>
          <ResponsiveTable columns={columns} data={filteredExpedientes} data-testid="expediente-table" rowTestIdKey="employee_id" rowTestIdPrefix="expediente-row" />

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginTop: "var(--space-md)",
            }}
          >
            <Button variant="secondary" size="sm" onClick={prevPage} disabled={offset === 0}>
              ← Anterior
            </Button>
            <span style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
              Página {Math.floor(offset / limit) + 1} de {Math.ceil(total / limit)}
            </span>
            <Button variant="secondary" size="sm" onClick={nextPage} disabled={offset + limit >= total}>
              Siguiente →
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

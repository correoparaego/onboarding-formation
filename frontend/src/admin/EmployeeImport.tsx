import { useState, useRef } from "react";
import { importApi } from "../api/endpoints";
import { Button, Card, Badge, Spinner } from "../components/ui";
import { useToast } from "../contexts/ToastContext";
import Breadcrumb from "../components/layout/Breadcrumb";

interface ImportReport {
  created: number;
  duplicates: number;
  errors: number;
  enrollments_created: number;
  report: Array<{
    row: number;
    status: "created" | "duplicate" | "rejected";
    dni?: string;
    reasons?: string[];
  }>;
}

export default function EmployeeImport() {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState<ImportReport | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const toast = useToast();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith(".xlsx") || droppedFile.name.endsWith(".xls"))) {
      setFile(droppedFile);
      setReport(null);
      setError("");
    } else {
      setError("Solo se aceptan archivos Excel (.xlsx, .xls)");
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setReport(null);
      setError("");
    }
  };

  const upload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setReport(null);
    try {
      const r = await importApi.upload(file);
      setReport(r.data);
      toast.success("Importación completada");
    } catch (e: any) {
      const msg = e?.response?.data?.error || "Error al importar el archivo";
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setReport(null);
    setError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const statusBadgeVariant = (status: string) => {
    switch (status) {
      case "created": return "success" as const;
      case "duplicate": return "warning" as const;
      case "rejected": return "danger" as const;
      default: return "neutral" as const;
    }
  };

  const statusLabel = (status: string) => {
    switch (status) {
      case "created": return "✓ Creado";
      case "duplicate": return "⚠ Duplicado";
      case "rejected": return "✗ Rechazado";
      default: return status;
    }
  };

  return (
    <div data-testid="import-page">
      <Breadcrumb items={[{ label: "Inicio", to: "/admin/dashboard" }, { label: "Importar empleados" }]} />
      <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-sm)" }}>Importar empleados</h2>
      <p style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)", marginBottom: "var(--space-lg)" }}>
        Sube un archivo Excel (.xlsx) con las columnas: <strong>dni, name, position, email, phone</strong> (opcional)
      </p>

      {loading ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "var(--space-md)", padding: "var(--space-2xl)" }}>
          <Spinner size={40} />
          <p style={{ color: "var(--color-text-secondary)" }}>Procesando archivo...</p>
        </div>
      ) : (
        <>
          {!report && (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              style={{
                border: `2px dashed ${dragging ? "var(--color-primary)" : "var(--color-border)"}`,
                borderRadius: "var(--radius-md)",
                padding: "var(--space-2xl)",
                textAlign: "center",
                cursor: "pointer",
                backgroundColor: dragging ? "var(--color-primary-light)" : "var(--color-bg-secondary)",
                transition: "all var(--transition-fast)",
                marginBottom: "var(--space-md)",
              }}
            >
              <input
                ref={fileInputRef}
                data-testid="file-input"
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileSelect}
                style={{ display: "none" }}
              />
              {file ? (
                <div>
                  <p style={{ fontSize: "var(--font-size-lg)", margin: 0 }}>📄 {file.name}</p>
                  <p style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)", margin: "var(--space-sm) 0 0 0" }}>
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              ) : (
                <div>
                  <p style={{ fontSize: "var(--font-size-lg)", margin: 0 }}>
                    {dragging ? "Suelta el archivo aquí" : "Arrastra un archivo Excel o haz clic para seleccionar"}
                  </p>
                  <p style={{ color: "var(--color-text-muted)", fontSize: "var(--font-size-sm)", margin: "var(--space-sm) 0 0 0" }}>
                    Formatos aceptados: .xlsx, .xls
                  </p>
                </div>
              )}
            </div>
          )}

          {file && !report && (
            <div style={{ display: "flex", gap: "var(--space-sm)", marginBottom: "var(--space-md)" }}>
              <Button data-testid="import-submit-btn" onClick={upload}>
                Importar empleados
              </Button>
              <Button variant="secondary" onClick={reset}>
                Cancelar
              </Button>
            </div>
          )}
        </>
      )}

      {error && (
        <p role="alert" aria-live="assertive" style={{ color: "var(--color-danger)", marginBottom: "var(--space-md)" }}>
          {error}
        </p>
      )}

      {report && (
        <div style={{ marginTop: "var(--space-lg)" }}>
          <h3 style={{ marginBottom: "var(--space-md)" }}>Resultado de la importación</h3>
          <div
            data-testid="import-result-stats"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
              gap: "var(--space-md)",
              marginBottom: "var(--space-lg)",
            }}
          >
            <Card style={{ background: "var(--color-success-bg)", textAlign: "center" }}>
              <div style={{ fontSize: "var(--font-size-3xl)", fontWeight: "bold", color: "var(--color-success-text)" }}>
                {report.created}
              </div>
              <div style={{ color: "var(--color-success-text)", fontSize: "var(--font-size-sm)" }}>Creados</div>
            </Card>
            <Card style={{ background: "var(--color-warning-bg)", textAlign: "center" }}>
              <div style={{ fontSize: "var(--font-size-3xl)", fontWeight: "bold", color: "var(--color-warning-text)" }}>
                {report.duplicates}
              </div>
              <div style={{ color: "var(--color-warning-text)", fontSize: "var(--font-size-sm)" }}>Duplicados</div>
            </Card>
            <Card style={{ background: "var(--color-danger-bg)", textAlign: "center" }}>
              <div style={{ fontSize: "var(--font-size-3xl)", fontWeight: "bold", color: "var(--color-danger-text)" }}>
                {report.errors}
              </div>
              <div style={{ color: "var(--color-danger-text)", fontSize: "var(--font-size-sm)" }}>Errores</div>
            </Card>
            <Card style={{ background: "var(--color-info-bg)", textAlign: "center" }}>
              <div style={{ fontSize: "var(--font-size-3xl)", fontWeight: "bold", color: "var(--color-info-text)" }}>
                {report.enrollments_created}
              </div>
              <div style={{ color: "var(--color-info-text)", fontSize: "var(--font-size-sm)" }}>Matrículas</div>
            </Card>
          </div>

          {report.report.length > 0 && (
            <div>
              <h4 style={{ marginBottom: "var(--space-sm)" }}>Detalle por fila</h4>
              <div style={{ maxHeight: 400, overflow: "auto", border: "1px solid var(--color-border)", borderRadius: "var(--radius-sm)" }}>
                <table data-testid="import-result-table" style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead style={{ background: "var(--color-bg-secondary)", position: "sticky", top: 0 }}>
                    <tr>
                      <th style={{ padding: "var(--space-sm)", textAlign: "left", borderBottom: "2px solid var(--color-border)" }}>Fila</th>
                      <th style={{ padding: "var(--space-sm)", textAlign: "left", borderBottom: "2px solid var(--color-border)" }}>DNI</th>
                      <th style={{ padding: "var(--space-sm)", textAlign: "left", borderBottom: "2px solid var(--color-border)" }}>Estado</th>
                      <th style={{ padding: "var(--space-sm)", textAlign: "left", borderBottom: "2px solid var(--color-border)" }}>Razón</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.report.map((row, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid var(--color-border-light)" }}>
                        <td style={{ padding: "var(--space-sm)" }}>{row.row}</td>
                        <td style={{ padding: "var(--space-sm)", fontFamily: "var(--font-mono)", fontSize: "var(--font-size-sm)" }}>{row.dni || "-"}</td>
                        <td style={{ padding: "var(--space-sm)" }}>
                          <Badge variant={statusBadgeVariant(row.status)} size="sm">
                            {statusLabel(row.status)}
                          </Badge>
                        </td>
                        <td style={{ padding: "var(--space-sm)", fontSize: "var(--font-size-sm)" }}>
                          {row.reasons?.join(", ") || "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <Button variant="secondary" onClick={reset} style={{ marginTop: "var(--space-md)" }}>
            Importar otro archivo
          </Button>
        </div>
      )}
    </div>
  );
}

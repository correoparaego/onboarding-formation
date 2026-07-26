import { useEffect, useState, ReactNode } from "react";

interface Column<T = any> {
  key: string;
  label: string;
  render?: (row: T) => ReactNode;
}

interface ResponsiveTableProps<T = any> {
  columns: Column<T>[];
  data: T[];
  mobileBreakpoint?: number;
  "data-testid"?: string;
  rowTestIdKey?: string;
  rowTestIdPrefix?: string;
}

export default function ResponsiveTable<T = any>({
  columns,
  data,
  mobileBreakpoint = 768,
  "data-testid": testId,
  rowTestIdKey,
  rowTestIdPrefix,
}: ResponsiveTableProps<T>) {
  const [isMobile, setIsMobile] = useState(
    typeof window !== "undefined" ? window.innerWidth < mobileBreakpoint : false
  );

  useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${mobileBreakpoint - 1}px)`);
    const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    setIsMobile(mql.matches);
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, [mobileBreakpoint]);

  if (data.length === 0) return null;

  if (isMobile) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-md)" }}>
        {data.map((row, rowIndex) => (
          <div
            key={rowIndex}
            data-testid={rowTestIdKey && rowTestIdPrefix ? `${rowTestIdPrefix}-${(row as any)[rowTestIdKey]}` : undefined}
            style={{
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-md)",
              padding: "var(--space-md)",
              background: "var(--color-bg)",
            }}
          >
            {columns.map((col) => (
              <div
                key={col.key}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  padding: "var(--space-xs) 0",
                  borderBottom: "1px solid var(--color-border-light)",
                  gap: "var(--space-sm)",
                }}
              >
                <span
                  style={{
                    fontSize: "var(--font-size-xs)",
                    color: "var(--color-text-muted)",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    flexShrink: 0,
                    minWidth: 80,
                  }}
                >
                  {col.label}
                </span>
                <span style={{ fontSize: "var(--font-size-sm)", textAlign: "right", flex: 1 }}>
                  {col.render ? col.render(row) : String((row as any)[col.key] ?? "-")}
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div style={{ border: "1px solid var(--color-border)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
      <div style={{ overflowX: "auto" }}>
        <table data-testid={testId} style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ background: "var(--color-bg-secondary)" }}>
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  style={{
                    padding: "var(--space-md)",
                    textAlign: "left",
                    borderBottom: "2px solid var(--color-border)",
                    fontSize: "var(--font-size-sm)",
                    fontWeight: 600,
                  }}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                data-testid={rowTestIdKey && rowTestIdPrefix ? `${rowTestIdPrefix}-${(row as any)[rowTestIdKey]}` : undefined}
                style={{ borderBottom: "1px solid var(--color-border-light)" }}
              >
                {columns.map((col) => (
                  <td key={col.key} style={{ padding: "var(--space-md)" }}>
                    {col.render ? col.render(row) : String((row as any)[col.key] ?? "-")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

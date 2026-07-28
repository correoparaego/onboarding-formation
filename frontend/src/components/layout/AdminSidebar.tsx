import { Link, useLocation } from "react-router-dom";
import { ThemeToggle } from "../ui";

interface AdminSidebarProps {
  onNavigate?: () => void;
  adminName?: string;
  onLogout?: () => void;
}

const navItems = [
  { to: "/admin/dashboard", label: "Dashboard", icon: "\uD83D\uDCCA" },
  { to: "/admin/import", label: "Importar empleados", icon: "\uD83D\uDCE5" },
  { to: "/admin/courses", label: "Cursos", icon: "\uD83D\uDCDA" },
  { to: "/admin/assignments", label: "Asignaciones", icon: "\uD83D\uDC65" },
  { to: "/admin/ai/key", label: "IA: Clave", icon: "\uD83D\uDD11" },
  { to: "/admin/ai/content", label: "IA: Contenido", icon: "\uD83E\uDD16" },
  { to: "/admin/ai/tests", label: "IA: Test PDF", icon: "\uD83D\uDCDD" },
  { to: "/admin/expediente", label: "Expediente", icon: "\uD83D\uDCCB" },
];

export default function AdminSidebar({ onNavigate, adminName, onLogout }: AdminSidebarProps) {
  const location = useLocation();

  return (
    <aside
      data-testid="admin-sidebar"
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        width: 240,
        background: "var(--color-bg-secondary)",
        borderRight: "1px solid var(--color-border-light)",
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: 100,
        overflowY: "auto",
      }}
    >
      <div
        style={{
          padding: "var(--space-lg) var(--space-md)",
          borderBottom: "1px solid var(--color-border-light)",
        }}
      >
        <h1 style={{ fontSize: "var(--font-size-lg)", fontWeight: 700 }}>Administración</h1>
      </div>

      <nav style={{ flex: 1, padding: "var(--space-sm)" }}>
        <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "var(--space-xs)" }}>
          {navItems.map((item) => {
            const isActive =
              location.pathname === item.to || location.pathname.startsWith(item.to + "/");
            return (
              <li key={item.to}>
                <Link
                  data-testid={`sidebar-link-${item.label.toLowerCase().replace(/\s+/g, "-")}`}
                  to={item.to}
                  onClick={onNavigate}
                  aria-current={isActive ? "page" : undefined}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "var(--space-sm)",
                    padding: "var(--space-sm) var(--space-md)",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "var(--font-size-sm)",
                    color: isActive ? "var(--color-primary)" : "var(--color-text-secondary)",
                    background: isActive ? "var(--color-primary-light)" : "transparent",
                    textDecoration: "none",
                    fontWeight: isActive ? 600 : 400,
                    transition: "background var(--transition-fast)",
                  }}
                >
                  <span aria-hidden="true" style={{ fontSize: "var(--font-size-lg)" }}>{item.icon}</span>
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div
        style={{
          padding: "var(--space-md)",
          borderTop: "1px solid var(--color-border-light)",
          display: "flex",
          flexDirection: "column",
          gap: "var(--space-sm)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)" }}>
            Hola, {adminName}
          </span>
          <ThemeToggle />
        </div>
        <button
          onClick={onLogout}
          style={{
            padding: "var(--space-sm) var(--space-md)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-sm)",
            color: "var(--color-text-secondary)",
            background: "var(--color-bg)",
            cursor: "pointer",
            fontSize: "var(--font-size-sm)",
            textAlign: "center",
          }}
        >
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}

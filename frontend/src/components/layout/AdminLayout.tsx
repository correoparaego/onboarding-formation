import { useState, useEffect, ReactNode } from "react";
import AdminSidebar from "./AdminSidebar";

interface AdminLayoutProps {
  children: ReactNode;
  adminName?: string;
  onLogout?: () => void;
}

export default function AdminLayout({ children, adminName, onLogout }: AdminLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const mql = window.matchMedia("(max-width: 767px)");
    const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    setIsMobile(mql.matches);
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);

  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [sidebarOpen]);

  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div style={{ minHeight: "100vh", background: "var(--color-bg)" }}>
      {isMobile && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            height: 56,
            background: "var(--color-bg-secondary)",
            borderBottom: "1px solid var(--color-border-light)",
            display: "flex",
            alignItems: "center",
            padding: "0 var(--space-md)",
            zIndex: 90,
            gap: "var(--space-md)",
          }}
        >
          <button
            onClick={() => setSidebarOpen(true)}
            aria-label="Abrir menú"
            style={{
              fontSize: "var(--font-size-2xl)",
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "var(--color-text)",
              padding: "var(--space-xs)",
              lineHeight: 1,
            }}
          >
            ☰
          </button>
          <span style={{ fontWeight: 600, fontSize: "var(--font-size-md)" }}>Administración</span>
        </div>
      )}

      {isMobile && sidebarOpen && (
        <div
          onClick={closeSidebar}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.5)",
            zIndex: 99,
          }}
        />
      )}

      {isMobile ? (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            bottom: 0,
            zIndex: 100,
            transform: sidebarOpen ? "translateX(0)" : "translateX(-100%)",
            transition: "transform var(--transition-normal)",
          }}
        >
          <AdminSidebar
            onNavigate={closeSidebar}
            adminName={adminName}
            onLogout={onLogout}
          />
        </div>
      ) : (
        <AdminSidebar adminName={adminName} onLogout={onLogout} />
      )}

      <main
        style={{
          padding: "var(--space-lg)",
          maxWidth: 1200,
          marginLeft: isMobile ? 0 : 240,
          paddingTop: isMobile ? "calc(var(--space-lg) + 56px)" : "var(--space-lg)",
        }}
      >
        {children}
      </main>
    </div>
  );
}

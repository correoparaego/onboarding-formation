import { useToast } from "../../contexts/ToastContext";

const typeStyles: Record<string, React.CSSProperties> = {
  success: { background: "var(--color-success-bg)", color: "var(--color-success-text)", borderLeft: "4px solid var(--color-success)" },
  error: { background: "var(--color-danger-bg)", color: "var(--color-danger-text)", borderLeft: "4px solid var(--color-danger)" },
  warning: { background: "var(--color-warning-bg)", color: "var(--color-warning-text)", borderLeft: "4px solid var(--color-warning)" },
  info: { background: "var(--color-info-bg)", color: "var(--color-info-text)", borderLeft: "4px solid var(--color-info)" },
};

const icons: Record<string, string> = {
  success: "✓",
  error: "✕",
  warning: "⚠",
  info: "ℹ",
};

export default function ToastContainer() {
  const { toasts, dismiss } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div
      aria-live="polite"
      style={{
        position: "fixed",
        top: "var(--space-lg)",
        right: "var(--space-lg)",
        zIndex: 2000,
        display: "flex",
        flexDirection: "column",
        gap: "var(--space-sm)",
        maxWidth: 380,
      }}
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          role="alert"
          style={{
            ...typeStyles[toast.type],
            padding: "var(--space-md)",
            borderRadius: "var(--radius-md)",
            boxShadow: "var(--shadow-md)",
            display: "flex",
            alignItems: "center",
            gap: "var(--space-sm)",
            animation: toast.exiting ? "toast-exit 0.3s ease forwards" : "toast-enter 0.3s ease",
            fontSize: "var(--font-size-sm)",
          }}
        >
          <span aria-hidden="true">{icons[toast.type]}</span>
          <span style={{ flex: 1 }}>{toast.message}</span>
          <button
            onClick={() => dismiss(toast.id)}
            aria-label="Cerrar notificación"
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "inherit",
              opacity: 0.7,
              fontSize: "var(--font-size-md)",
              padding: 0,
              lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}

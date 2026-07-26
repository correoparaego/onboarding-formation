import { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "var(--space-lg)", textAlign: "center", minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-md)" }}>Algo salió mal</h2>
          <p role="alert" style={{ color: "var(--color-text-secondary)", marginBottom: "var(--space-md)" }}>
            Ha ocurrido un error inesperado. Por favor, recarga la página.
          </p>
          {import.meta.env.DEV && this.state.error && (
            <details style={{ marginTop: "var(--space-md)", textAlign: "left", maxWidth: 600 }}>
              <summary style={{ cursor: "pointer", color: "var(--color-primary)" }}>Detalles del error (solo desarrollo)</summary>
              <pre style={{ fontSize: "var(--font-size-xs)", overflow: "auto", background: "var(--color-bg-secondary)", padding: "var(--space-md)", borderRadius: "var(--radius-sm)", marginTop: "var(--space-sm)" }}>
                {this.state.error.toString()}
              </pre>
            </details>
          )}
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: "var(--space-md)",
              padding: "var(--space-sm) var(--space-lg)",
              background: "var(--color-primary)",
              color: "#fff",
              border: "none",
              borderRadius: "var(--radius-sm)",
              cursor: "pointer",
              fontSize: "var(--font-size-md)",
            }}
          >
            Recargar página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

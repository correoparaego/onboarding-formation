import { ReactNode } from "react";

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  "data-testid"?: string;
}

export default function EmptyState({ icon, title, description, action, "data-testid": testId }: EmptyStateProps) {
  return (
    <div
      data-testid={testId || "empty-state"}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "var(--space-2xl)",
        textAlign: "center",
        color: "var(--color-text-secondary)",
      }}
    >
      {icon && (
        <div style={{ fontSize: 48, marginBottom: "var(--space-md)", opacity: 0.5 }}>
          {icon}
        </div>
      )}
      <h3 style={{ fontSize: "var(--font-size-lg)", color: "var(--color-text)", marginBottom: "var(--space-sm)" }}>
        {title}
      </h3>
      {description && (
        <p style={{ fontSize: "var(--font-size-sm)", maxWidth: 400, marginBottom: "var(--space-lg)" }}>
          {description}
        </p>
      )}
      {action || null}
    </div>
  );
}

interface ProgressBarProps {
  value: number;
  label?: string;
  showPercentage?: boolean;
}

export default function ProgressBar({ value, label, showPercentage = false }: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div style={{ width: "100%" }}>
      {(label || showPercentage) && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "var(--space-xs)",
            fontSize: "var(--font-size-sm)",
            color: "var(--color-text-secondary)",
          }}
        >
          {label && <span>{label}</span>}
          {showPercentage && <span>{Math.round(clamped)}%</span>}
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || "Progreso"}
        style={{
          width: "100%",
          height: 8,
          background: "var(--color-bg-tertiary)",
          borderRadius: "var(--radius-full)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${clamped}%`,
            height: "100%",
            background: "var(--color-primary)",
            borderRadius: "var(--radius-full)",
            transition: "width var(--transition-normal)",
          }}
        />
      </div>
    </div>
  );
}

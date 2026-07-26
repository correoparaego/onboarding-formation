interface SpinnerProps {
  size?: number;
}

export default function Spinner({ size = 24 }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label="Cargando"
      style={{
        display: "inline-block",
        width: size,
        height: size,
        border: `${Math.max(2, size / 8)}px solid var(--color-border)`,
        borderTopColor: "var(--color-primary)",
        borderRadius: "50%",
        animation: "spin 0.6s linear infinite",
      }}
    >
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </span>
  );
}

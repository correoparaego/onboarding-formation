import { forwardRef, InputHTMLAttributes, ReactNode } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  icon?: ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, hint, icon, id, style, ...rest },
  ref
) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-xs)", ...style }}>
      {label && (
        <label
          htmlFor={inputId}
          style={{ fontSize: "var(--font-size-sm)", fontWeight: 500, color: "var(--color-text)" }}
        >
          {label}
        </label>
      )}
      <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
        {icon && (
          <span
            style={{
              position: "absolute",
              left: "var(--space-sm)",
              color: "var(--color-text-muted)",
              pointerEvents: "none",
            }}
          >
            {icon}
          </span>
        )}
        <input
          ref={ref}
          id={inputId}
          style={{
            width: "100%",
            paddingLeft: icon ? "var(--space-xl)" : undefined,
            borderColor: error ? "var(--color-danger)" : undefined,
          }}
          {...rest}
        />
      </div>
      {error && (
        <span role="alert" style={{ fontSize: "var(--font-size-xs)", color: "var(--color-danger)" }}>
          {error}
        </span>
      )}
      {hint && !error && (
        <span style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
          {hint}
        </span>
      )}
    </div>
  );
});

export default Input;

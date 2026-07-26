import { HTMLAttributes } from "react";

type Variant = "success" | "warning" | "danger" | "info" | "neutral";
type Size = "sm" | "md";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: Variant;
  size?: Size;
}

const variantStyles: Record<Variant, React.CSSProperties> = {
  success: { background: "var(--color-success-bg)", color: "var(--color-success-text)" },
  warning: { background: "var(--color-warning-bg)", color: "var(--color-warning-text)" },
  danger: { background: "var(--color-danger-bg)", color: "var(--color-danger-text)" },
  info: { background: "var(--color-info-bg)", color: "var(--color-info-text)" },
  neutral: { background: "var(--color-bg-tertiary)", color: "var(--color-text-secondary)" },
};

const sizeStyles: Record<Size, React.CSSProperties> = {
  sm: { padding: "2px 6px", fontSize: "var(--font-size-xs)" },
  md: { padding: "4px 8px", fontSize: "var(--font-size-sm)" },
};

export default function Badge({
  variant = "neutral",
  size = "md",
  style,
  children,
  ...rest
}: BadgeProps) {
  return (
    <span
      style={{
        display: "inline-block",
        borderRadius: "var(--radius-full)",
        fontWeight: 600,
        lineHeight: 1.4,
        whiteSpace: "nowrap",
        ...variantStyles[variant],
        ...sizeStyles[size],
        ...style,
      }}
      {...rest}
    >
      {children}
    </span>
  );
}

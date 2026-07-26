import { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: "none" | "sm" | "md" | "lg";
  hoverable?: boolean;
  children: ReactNode;
}

const paddingMap = {
  none: "0",
  sm: "var(--space-sm)",
  md: "var(--space-md)",
  lg: "var(--space-lg)",
};

export default function Card({
  padding = "md",
  hoverable = false,
  children,
  style,
  ...rest
}: CardProps) {
  return (
    <div
      style={{
        background: "var(--color-bg)",
        border: "1px solid var(--color-border-light)",
        borderRadius: "var(--radius-md)",
        boxShadow: "var(--shadow-sm)",
        padding: paddingMap[padding],
        transition: "box-shadow var(--transition-fast), transform var(--transition-fast)",
        cursor: hoverable ? "pointer" : undefined,
        ...style,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}

import { Link } from "react-router-dom";

interface BreadcrumbItem {
  label: string;
  to?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export default function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav aria-label="Breadcrumb" style={{ marginBottom: "var(--space-md)" }}>
      <ol
        style={{
          listStyle: "none",
          padding: 0,
          display: "flex",
          alignItems: "center",
          gap: "var(--space-xs)",
          fontSize: "var(--font-size-sm)",
          flexWrap: "wrap",
        }}
      >
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={index} style={{ display: "flex", alignItems: "center", gap: "var(--space-xs)" }}>
              {index > 0 && (
                <span style={{ color: "var(--color-text-muted)" }} aria-hidden="true">
                  /
                </span>
              )}
              {isLast || !item.to ? (
                <span style={{ color: "var(--color-text-secondary)", fontWeight: isLast ? 500 : 400 }}>
                  {item.label}
                </span>
              ) : (
                <Link
                  to={item.to}
                  style={{
                    color: "var(--color-primary)",
                    textDecoration: "none",
                  }}
                >
                  {item.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

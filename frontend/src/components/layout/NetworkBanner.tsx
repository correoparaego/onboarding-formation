import { useEffect, useState } from "react";

export default function NetworkBanner() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [justRestored, setJustRestored] = useState(false);

  useEffect(() => {
    const handleOffline = () => {
      setIsOnline(false);
      setJustRestored(false);
    };

    const handleOnline = () => {
      setIsOnline(true);
      setJustRestored(true);
      const timer = setTimeout(() => setJustRestored(false), 3000);
      return () => clearTimeout(timer);
    };

    window.addEventListener("offline", handleOffline);
    window.addEventListener("online", handleOnline);
    return () => {
      window.removeEventListener("offline", handleOffline);
      window.removeEventListener("online", handleOnline);
    };
  }, []);

  if (!isOnline) {
    return (
      <div
        data-testid="network-banner"
        role="alert"
        aria-live="assertive"
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 9999,
          padding: "var(--space-sm) var(--space-md)",
          background: "var(--color-danger)",
          color: "#fff",
          textAlign: "center",
          fontSize: "var(--font-size-sm)",
          fontWeight: 600,
        }}
      >
        Sin conexión a internet. Verificando...
      </div>
    );
  }

  if (justRestored) {
    return (
      <div
        role="status"
        aria-live="polite"
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 9999,
          padding: "var(--space-sm) var(--space-md)",
          background: "var(--color-success)",
          color: "#fff",
          textAlign: "center",
          fontSize: "var(--font-size-sm)",
          fontWeight: 600,
          animation: "toast-exit 0.5s ease 2.5s forwards",
        }}
      >
        Conexión restaurada
      </div>
    );
  }

  return null;
}

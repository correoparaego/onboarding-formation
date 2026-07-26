import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { aiApi } from "../../api/endpoints";
import { Button, Input, Card, Badge } from "../../components/ui";
import { useToast } from "../../contexts/ToastContext";

const keySchema = z.object({
  provider: z.string().min(1, "Proveedor es obligatorio"),
  base_url: z.string().url("URL inválida").min(1, "Base URL es obligatoria"),
  model: z.string().min(1, "Modelo es obligatorio"),
  api_key: z.string().min(1, "API key es obligatoria"),
});

type KeyFormData = z.infer<typeof keySchema>;

export default function AiKeyForm() {
  const [status, setStatus] = useState<{ has_key: boolean; status: string | null; provider?: string; model?: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusLoading, setStatusLoading] = useState(true);
  const toast = useToast();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<KeyFormData>({
    resolver: zodResolver(keySchema),
  });

  useEffect(() => {
    aiApi
      .keyStatus()
      .then((r) => setStatus(r.data))
      .catch((e) => toast.error(e?.response?.data?.error || "Error al cargar el estado de la clave"))
      .finally(() => setStatusLoading(false));
  }, []);

  const submit = async (data: KeyFormData) => {
    setLoading(true);
    try {
      await aiApi.setKey(data);
      reset({ provider: data.provider, base_url: data.base_url, model: data.model, api_key: "" });
      const r = await aiApi.keyStatus();
      setStatus(r.data);
      toast.success("Clave guardada correctamente");
    } catch (e: any) {
      toast.error(e?.response?.data?.error || "Error al guardar la clave.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ fontSize: "var(--font-size-2xl)", marginBottom: "var(--space-md)" }}>Clave de LLM (BYO)</h2>
      {statusLoading ? (
        <p style={{ color: "var(--color-text-muted)" }}>Cargando...</p>
      ) : status?.has_key ? (
        <Card style={{ marginBottom: "var(--space-lg)", background: "var(--color-bg-secondary)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-sm)" }}>
            <span style={{ color: "var(--color-text-secondary)" }}>Clave activa:</span>
            <Badge variant="success">{status.provider}</Badge>
            <span>/ {status.model}</span>
            <Badge variant={status.status === "ok" ? "success" : "warning"} size="sm">
              {status.status}
            </Badge>
          </div>
        </Card>
      ) : (
        <Card style={{ marginBottom: "var(--space-lg)", background: "var(--color-warning-bg)" }}>
          <p style={{ color: "var(--color-warning-text)" }}>No hay clave configurada.</p>
        </Card>
      )}
      <Card>
        <form data-testid="ai-key-form" onSubmit={handleSubmit(submit)} style={{ display: "grid", gap: "var(--space-md)", maxWidth: 420 }}>
          <Input
            label="Proveedor"
            {...register("provider")}
            placeholder="openai, groq, ollama"
            error={errors.provider?.message}
          />
          <Input
            label="Base URL"
            {...register("base_url")}
            placeholder="https://.../v1"
            error={errors.base_url?.message}
          />
          <Input
            label="Modelo"
            {...register("model")}
            placeholder="gpt-4o-mini"
            error={errors.model?.message}
          />
          <Input
            data-testid="api-key-input"
            label="API key"
            type="password"
            {...register("api_key")}
            error={errors.api_key?.message}
          />
          <Button data-testid="save-key-btn" type="submit" disabled={loading}>
            {loading ? "Guardando..." : "Guardar clave"}
          </Button>
        </form>
      </Card>
    </div>
  );
}

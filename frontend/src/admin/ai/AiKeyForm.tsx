import { useEffect, useState } from "react";
import { aiApi } from "../../api/endpoints";

// Admin BYO LLM key entry (spec ai-generation §BYO). The raw key is sent to the
// server and never returned; the UI only shows status (active/inactive) and
// provider/model, never the secret.
export default function AiKeyForm() {
  const [provider, setProvider] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [model, setModel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [status, setStatus] = useState<{ has_key: boolean; status: string | null; provider?: string; model?: string } | null>(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    aiApi.keyStatus().then((r) => setStatus(r.data)).catch(() => setStatus(null));
  }, []);

  const submit = async () => {
    setMsg("");
    try {
      await aiApi.setKey({ provider, base_url: baseUrl, model, api_key: apiKey });
      setApiKey(""); // never retain the raw key in the UI
      const r = await aiApi.keyStatus();
      setStatus(r.data);
      setMsg("Clave guardada (cifrada en servidor).");
    } catch (e) {
      setMsg("Error al guardar la clave.");
    }
  };

  return (
    <div>
      <h2>Clave de LLM (BYO)</h2>
      {status?.has_key ? (
        <p>
          Clave activa: <b>{status.provider}</b> / {status.model} ({status.status})
        </p>
      ) : (
        <p>No hay clave configurada.</p>
      )}
      <div style={{ display: "grid", gap: 8, maxWidth: 420 }}>
        <input placeholder="Proveedor (openai/groq/ollama)" value={provider} onChange={(e) => setProvider(e.target.value)} />
        <input placeholder="Base URL (https://.../v1)" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} />
        <input placeholder="Modelo (gpt-4o-mini)" value={model} onChange={(e) => setModel(e.target.value)} />
        <input type="password" placeholder="API key" value={apiKey} onChange={(e) => setApiKey(e.target.value)} />
        <button onClick={submit} disabled={!provider || !baseUrl || !model || !apiKey}>
          Guardar clave
        </button>
      </div>
      {msg && <p>{msg}</p>}
    </div>
  );
}

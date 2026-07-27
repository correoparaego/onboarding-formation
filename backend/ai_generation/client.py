"""OpenAI-compatible LLM client (spec ai-generation §OpenAI-Compatible Client).

A single interface (`LLMClient.chat`) parameterised by (base_url, api_key,
model) covers OpenAI, Groq, Together, and Ollama-local without per-provider
branching. The real implementation speaks the OpenAI `/chat/completions`
contract over HTTP (stdlib only, no hard dependency on the `openai` package).
A `FakeLLMClient` is provided so tests NEVER call a real provider.
"""
import json
import urllib.request

from django.conf import settings


class LLMClient:
    """Abstract client. Subclasses implement `chat`."""

    def chat(self, messages, **kwargs) -> str:
        raise NotImplementedError


class OpenAICompatibleClient(LLMClient):
    """Talks to any OpenAI-compatible `/chat/completions` endpoint."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def chat(self, messages, **kwargs) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.2),
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001 - surface as generation error
            raise RuntimeError(f"LLM request failed: {exc}") from exc


class GeminiClient(LLMClient):
    """Google Gemini API client (default fallback when admin has no BYO key)."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model

    def chat(self, messages, **kwargs) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # Convert OpenAI-style messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.2),
            },
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return body["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as exc:
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc


class FakeLLMClient(LLMClient):
    """Deterministic stand-in for tests. Never performs network I/O."""

    def __init__(self, mode: str = "content"):
        # mode: "content" -> course draft; "tests" -> question-bank draft.
        self.mode = mode

    def chat(self, messages, **kwargs) -> str:
        if self.mode == "tests":
            return json.dumps(
                {
                    "questions": [
                        {
                            "text": "¿Cuál es el objetivo de la formación?",
                            "options": [
                                "Cumplir la normativa",
                                "Ocio",
                                "Competencia",
                                "Ninguna",
                            ],
                            "correct_index": 0,
                        },
                        {
                            "text": "¿Quién debe completarla?",
                            "options": ["El empleado", "El cliente", "Nadie", "El proveedor"],
                            "correct_index": 0,
                        },
                    ]
                }
            )
        return json.dumps(
            {
                "title": "Formación Inicial de Seguridad",
                "sections": [
                    {
                        "order": 1,
                        "title": "Introducción",
                        "content": "Bienvenido a la formación inicial.",
                        "section_base": 120,
                    },
                    {
                        "order": 2,
                        "title": "Normativa",
                        "content": "Resumen de la normativa aplicable.",
                        "section_base": 180,
                    },
                ],
            }
        )


def make_client(mode: str, admin_user=None) -> LLMClient:
    """Factory: returns a fake client (tests), admin BYO key, or Gemini default."""
    if getattr(settings, "AI_USE_FAKE_LLM", False):
        return FakeLLMClient(mode=mode)
    
    # Try admin's BYO key first
    from .models import AdminLLMKey
    key_row = AdminLLMKey.objects.filter(admin=admin_user, status="active").first()
    if key_row is not None:
        return OpenAICompatibleClient(
            key_row.base_url, key_row.get_raw_key(), key_row.model
        )
    
    # Fall back to Gemini default
    gemini_key = getattr(settings, "GEMINI_API_KEY", None)
    if gemini_key:
        gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        return GeminiClient(gemini_key, gemini_model)
    
    raise RuntimeError(
        "no LLM key configured. Either set GEMINI_API_KEY environment variable "
        "or configure your own LLM key via the admin interface."
    )

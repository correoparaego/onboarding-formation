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
    """Factory: returns a fake client (tests) or a real OpenAI-compatible one."""
    if getattr(settings, "AI_USE_FAKE_LLM", False):
        return FakeLLMClient(mode=mode)
    from .models import AdminLLMKey

    key_row = AdminLLMKey.objects.filter(admin=admin_user, status="active").first()
    if key_row is None:
        raise RuntimeError("no active LLM key configured for this admin")
    return OpenAICompatibleClient(
        key_row.base_url, key_row.get_raw_key(), key_row.model
    )

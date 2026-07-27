"""OpenAI-compatible LLM client (spec ai-generation §OpenAI-Compatible Client).

A single interface (`LLMClient.chat`) parameterised by (base_url, api_key,
model) covers OpenAI, Groq, Together, and Ollama-local without per-provider
branching. The real implementation speaks the OpenAI `/chat/completions`
contract over HTTP (stdlib only, no hard dependency on the `openai` package).
A `FakeLLMClient` is provided so tests NEVER call a real provider.
"""
import json
import urllib.error
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

    def validate_configuration(self) -> None:
        """Verify the API key and model without generating billable content."""
        req = urllib.request.Request(
            f"{self.base_url}/models",
            headers={"Authorization": f"Bearer {self.api_key}"},
            method="GET",
        )
        body = _request_json(req, "LLM", timeout=30)
        if not isinstance(body, dict) or not isinstance(body.get("data"), list):
            raise RuntimeError("LLM returned an unexpected models response format")
        model_ids = {
            item.get("id")
            for item in body["data"]
            if isinstance(item, dict) and item.get("id")
        }
        if self.model not in model_ids:
            raise RuntimeError(
                f"LLM model '{self.model}' is not available for this API key"
            )

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
        body = _request_json(req, "LLM")
        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("LLM returned an unexpected response format") from exc


class GeminiClient(LLMClient):
    """Google Gemini API client (default fallback when admin has no BYO key)."""

    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
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
        body = _request_json(req, "Gemini")
        try:
            return body["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Gemini returned an unexpected response format") from exc


def _request_json(req, provider: str, timeout: int = 60) -> dict:
    """Send a provider request while preserving its useful error message."""
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        message = _provider_error_message(exc)
        raise RuntimeError(
            f"{provider} request failed ({exc.code}): {message}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{provider} connection failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"{provider} connection timed out") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{provider} returned an invalid JSON response") from exc


def _provider_error_message(exc: urllib.error.HTTPError) -> str:
    try:
        body = json.loads(exc.read().decode("utf-8"))
        error = body.get("error", body)
        if isinstance(error, dict):
            return str(error.get("message") or error.get("status") or "provider error")
        return str(error)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "provider error"


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
        gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-3.6-flash")
        return GeminiClient(gemini_key, gemini_model)
    
    raise RuntimeError(
        "no LLM key configured. Either set GEMINI_API_KEY environment variable "
        "or configure your own LLM key via the admin interface."
    )

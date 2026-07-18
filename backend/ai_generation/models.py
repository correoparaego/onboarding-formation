"""AI generation models (spec ai-generation).

``AdminLLMKey`` stores a per-admin, BYO LLM API key encrypted at rest. The raw
key is NEVER persisted in plaintext and is only decrypted server-side during a
generation call. API responses never include the raw key (nor the ciphertext),
and the key is never accessed on any employee route (enforced by the
RoleIsolationMiddleware on ``/api/ai/``).
"""
from django.conf import settings
from django.db import models

from common.crypto import decrypt_value, encrypt_value


class AdminLLMKey(models.Model):
    STATUS_CHOICES = [
        ("active", "active"),
        ("inactive", "inactive"),
    ]

    # One credential store per admin (BYO key). One-to-one so an admin can hold
    # at most a single active provider config at a time.
    admin = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="llm_key",
    )
    # Raw key encrypted at rest (deterministic envelope from common.crypto).
    encrypted_key = models.TextField()
    provider = models.CharField(max_length=80, help_text="Provider label, e.g. openai/groq/ollama")
    base_url = models.URLField(max_length=400, help_text="OpenAI-compatible base URL")
    model = models.CharField(max_length=120, help_text="Model name")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "admin LLM key"
        verbose_name_plural = "admin LLM keys"

    def __str__(self):
        return f"{self.admin_id} -> {self.provider}/{self.model} ({self.status})"

    # -- Encryption helpers (server-side only) -----------------------------
    def set_raw_key(self, raw_key: str) -> None:
        """Encrypt and store the raw key. Caller MUST discard ``raw_key``."""
        self.encrypted_key = encrypt_value(raw_key)

    def get_raw_key(self) -> str:
        """Decrypt the raw key. NEVER serialize the result to a response."""
        return decrypt_value(self.encrypted_key)

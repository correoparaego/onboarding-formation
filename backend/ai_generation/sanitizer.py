"""PII-exclusion sanitizer (spec ai-generation §PII; design §PII Guard).

HARD DESIGN CONSTRAINT: the prompt builder assembles LLM prompts ONLY from
course content, admin reference documents, and extracted PDF text. Employee
PII (DNI, name, email, phone) is structurally excluded.

This module is the defense-in-depth safety net. It redacts employee-style PII
from arbitrary text. Critically, it has NO access to the Employee queryset:
this file does not import ``employees`` and operates purely on text patterns,
so it is impossible for it to leak a specific employee record. The guard is
enforced by construction, not by an optional flag.
"""
import re

# Spanish DNI: 8 digits + control letter.
_DNI_RE = re.compile(r"\b\d{8}[A-Za-z]\b")
# Email addresses.
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# Spanish phone: optional +34, 9 digits with optional separators.
_PHONE_RE = re.compile(r"(?:\+34[\s]?)?\d{3}[\s.\-]?\d{3}[\s.\-]?\d{3}\b")
# Name labels: "Nombre:" / "Name:" followed by one or two capitalised words.
_NAME_RE = re.compile(
    r"(?:nombre|name)\s*[:=]\s*"
    r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?",
    re.IGNORECASE,
)

_REDACT = "[REDACTED]"

_PATTERNS = (_DNI_RE, _EMAIL_RE, _PHONE_RE, _NAME_RE)


def sanitize_text(text: str) -> str:
    """Return ``text`` with any employee-style PII redacted.

    Operates only on textual patterns. Does not, and cannot, consult the
    Employee table — this module never imports it.
    """
    if not text:
        return text
    cleaned = text
    for pattern in _PATTERNS:
        cleaned = pattern.sub(_REDACT, cleaned)
    return cleaned


def sanitize_many(texts) -> list:
    """Sanitize an iterable of text fragments."""
    return [sanitize_text(t) if isinstance(t, str) else t for t in texts]

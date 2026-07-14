"""Authentication models for MVP Formación Inicial.

Admins reuse Django's built-in ``User`` (staff). Employees authenticate via a
single-use, time-limited magic-link/code token (see secure-access / spec
authentication). The raw token/code is NEVER persisted or logged — only a
SHA-256 hash is stored, so redemption requires presenting the original value
which is returned exactly once at issuance time.
"""
import datetime
import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from employees.models import Employee


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class EmployeeAccessToken(models.Model):
    """A single-use access token/code issued for an employee's training.

    The same secret is exposed two ways: a long ``token`` (for a magic link)
    and a short ``code`` (for manual entry). Both are stored ONLY as hashes;
    the raw values exist solely in the issuance response and are never written
    to the DB, logs, or audit (spec secure-access §Token Delivery).
    """

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="access_tokens"
    )
    # Optional link to the enrollment that triggered issuance (secure-access,
    # Phase 8). Nullable now so Phase 3 can ship without enrollment wiring.
    enrollment = models.ForeignKey(
        "reading_gate.Enrollment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="access_tokens",
    )
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    code_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"token for {self.employee_id} (expires {self.expires_at})"

    # -- Issuance ---------------------------------------------------------
    @classmethod
    def issue(cls, employee, enrollment=None, ttl_seconds=None):
        """Create a token and return ``(instance, raw_token, code)``.

        The raw values are returned exactly once and MUST be delivered to the
        employee (Phase 8). They are never stored.
        """
        ttl = ttl_seconds or getattr(
            settings, "EMPLOYEE_TOKEN_TTL_SECONDS", 60 * 60 * 24
        )
        raw_token = secrets.token_urlsafe(32)
        code = secrets.token_hex(4)  # 8 hex chars, low collision risk
        instance = cls.objects.create(
            employee=employee,
            enrollment=enrollment,
            token_hash=_hash(raw_token),
            code_hash=_hash(code),
            expires_at=timezone.now() + datetime.timedelta(seconds=ttl),
        )
        return instance, raw_token, code

    # -- Redemption -------------------------------------------------------
    @classmethod
    def redeem(cls, value):
        """Redeem a presented ``token`` or ``code``.

        Returns ``(employee, "ok")`` on success, or ``(None, reason)`` with
        reason in {"invalid", "consumed", "expired"}. Marks the token consumed
        atomically enough for MVP (single attempt per request).
        """
        if not isinstance(value, str) or not value:
            return None, "invalid"
        digest = _hash(value)
        now = timezone.now()
        token = cls.objects.filter(token_hash=digest).first()
        if token is None:
            token = cls.objects.filter(code_hash=digest).first()
        if token is None:
            return None, "invalid"
        if token.consumed_at is not None:
            return None, "consumed"
        if token.expires_at < now:
            return None, "expired"
        token.consumed_at = now
        token.save(update_fields=["consumed_at"])
        return token.employee, "ok"

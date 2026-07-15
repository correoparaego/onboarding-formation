"""Configurable email transport (spec notifications §Configurable Email Transport).

Abstracts the send backend so switching Resend <-> SMTP requires NO code change,
only configuration (settings.EMAIL_TRANSPORT). A ``console`` transport is the
local default so delivery can be verified without credentials (spec §Spanish
Templates / §Delivery Logging).
"""
import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class EmailResult:
    def __init__(self, ok, detail=""):
        self.ok = ok
        self.detail = detail


class ConsoleEmailTransport:
    """Prints the email to stdout. Local default; safe, no network."""

    name = "console"

    def send(self, subject, body, recipient, from_email=None):
        from_email = from_email or getattr(
            settings, "DEFAULT_FROM_EMAIL", "no-reply@formacion.local"
        )
        print(
            f"\n[email:console] to={recipient} from={from_email} subject={subject}\n{body}\n"
        )
        return EmailResult(True, "console")


class SMTPEmailTransport:
    """Uses Django's configured SMTP backend (django.core.mail.send_mail)."""

    name = "smtp"

    def send(self, subject, body, recipient, from_email=None):
        from_email = from_email or getattr(
            settings, "DEFAULT_FROM_EMAIL", "no-reply@formacion.local"
        )
        try:
            send_mail(subject, body, from_email, [recipient], fail_silently=False)
            return EmailResult(True, "smtp")
        except Exception as exc:  # best-effort delivery, never crash caller
            logger.warning("SMTP send failed: %s", exc)
            return EmailResult(False, str(exc)[:255])


class ResendEmailTransport:
    """Sends via the Resend API. Requires the ``resend`` package + RESEND_API_KEY."""

    name = "resend"

    def send(self, subject, body, recipient, from_email=None):
        from_email = from_email or getattr(
            settings, "DEFAULT_FROM_EMAIL", "no-reply@formacion.local"
        )
        try:
            import resend  # lazy import — optional dependency
        except ImportError:
            return EmailResult(False, "resend package not installed")
        api_key = getattr(settings, "RESEND_API_KEY", "")
        if not api_key:
            return EmailResult(False, "RESEND_API_KEY not configured")
        try:
            resend.api_key = api_key
            resend.Emails.send(
                {"from": from_email, "to": [recipient], "subject": subject, "text": body}
            )
            return EmailResult(True, "resend")
        except Exception as exc:
            logger.warning("Resend send failed: %s", exc)
            return EmailResult(False, str(exc)[:255])


def get_transport():
    """Return the configured transport. Defaults to console (local verification)."""
    transport = getattr(settings, "EMAIL_TRANSPORT", "console").lower()
    if transport == "smtp":
        return SMTPEmailTransport()
    if transport == "resend":
        return ResendEmailTransport()
    return ConsoleEmailTransport()

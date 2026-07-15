"""Secure-access issuance + notification delivery (spec secure-access, notifications).

Token issuance reuses ``authentication.EmployeeAccessToken`` (single-use, TTL,
only hashes stored — raw values exist solely in the issuance response). Delivery
is best-effort: a send failure is logged but NEVER blocks token issuance or
enrollment assignment. Raw token/code are returned to the caller for delivery and
are NEVER written to ``NotificationLog`` or any audit payload (spec §Delivery Logging).
"""
import logging

from django.utils import timezone

from authentication.models import EmployeeAccessToken
from notifications.models import NotificationLog
from notifications.templates import access_email, completion_email, reminder_email
from notifications.transports import get_transport

logger = logging.getLogger(__name__)


def _deliver(template, employee, subject, body):
    """Best-effort delivery; always records a NotificationLog (no secrets)."""
    if not employee.email:
        NotificationLog.objects.create(
            recipient="", template=template, status="skipped", detail="no recipient email"
        )
        return False
    result = get_transport().send(subject, body, employee.email)
    NotificationLog.objects.create(
        recipient=employee.email,
        template=template,
        status="sent" if result.ok else "failed",
        detail=result.detail or "",
    )
    return result.ok


def issue_access_token(enrollment):
    """Issue a fresh single-use token for the enrollment and email it.

    Returns ``(raw_token, code)`` for the caller to deliver, or ``(None, None)``
    if the employee has no email (token is still issued; delivery is skipped).
    """
    employee = enrollment.employee
    _, raw_token, code = EmployeeAccessToken.issue(employee, enrollment=enrollment)
    subject, body = access_email(employee, raw_token, code)
    _deliver("access", employee, subject, body)
    return raw_token, code


def resend_access_token(enrollment):
    """Idempotent resend (spec secure-access §Token Delivery).

    Any previously unconsumed, unexpired token for this enrollment is invalidated
    (marked consumed) so exactly ONE active token exists, then a fresh token is
    issued and emailed. Repeated resends simply rotate the active token rather
    than leaving multiple valid links in the wild.
    """
    employee = enrollment.employee
    now = timezone.now()
    EmployeeAccessToken.objects.filter(
        employee=employee,
        enrollment=enrollment,
        consumed_at__isnull=True,
        expires_at__gt=now,
    ).update(consumed_at=now)
    return issue_access_token(enrollment)


def send_reminder(enrollment):
    """Issue a fresh token and send the Spanish reminder email."""
    employee = enrollment.employee
    _, raw_token, code = EmployeeAccessToken.issue(employee, enrollment=enrollment)
    subject, body = reminder_email(employee, raw_token, code)
    _deliver("reminder", employee, subject, body)
    return raw_token, code


def send_completion(enrollment):
    """Send the Spanish completion email (no token involved)."""
    employee = enrollment.employee
    subject, body = completion_email(employee, enrollment.course.title)
    _deliver("completion", employee, subject, body)

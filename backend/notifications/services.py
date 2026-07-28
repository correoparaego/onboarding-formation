"""Secure-access issuance + notification delivery (spec secure-access, notifications).

Token issuance reuses ``authentication.EmployeeAccessToken`` (single-use, TTL,
only hashes stored — raw values exist solely in the issuance response). Delivery
is best-effort: a send failure is logged but NEVER blocks token issuance or
enrollment assignment. Raw token/code are returned to the caller for delivery and
are NEVER written to ``NotificationLog`` or any audit payload (spec §Delivery Logging).
"""
import logging

from django.db import transaction
from django.utils import timezone

from authentication.models import EmployeeAccessToken
from notifications.models import NotificationLog
from notifications.templates import access_email, completion_email, reminder_email
from notifications.transports import get_transport

logger = logging.getLogger(__name__)


def _record_delivery(template, employee, status, detail):
    try:
        NotificationLog.objects.create(
            recipient=employee.email,
            template=template,
            status=status,
            detail=detail or "",
        )
    except Exception as exc:
        logger.warning("notification delivery log failed: %s", exc)


def _deliver(template, employee, subject, body, allow_console=True):
    """Best-effort delivery; always records a NotificationLog (no secrets)."""
    if not employee.email:
        _record_delivery(template, employee, "skipped", "no recipient email")
        from notifications.transports import EmailResult

        return EmailResult(False, "no recipient email")
    transport = get_transport()
    if transport.name == "console" and not allow_console:
        from notifications.transports import EmailResult

        result = EmailResult(False, "console transport disabled for access secrets")
    else:
        result = transport.send(subject, body, employee.email)
    _record_delivery(
        template, employee, "sent" if result.ok else "failed", result.detail
    )
    return result


@transaction.atomic
def rotate_employee_access(employee, enrollment=None):
    """Invalidate active employee access and return a fresh secret exactly once."""
    from employees.models import Employee

    employee = Employee.objects.select_for_update().get(pk=employee.pk)
    now = timezone.now()
    EmployeeAccessToken.objects.filter(
        employee=employee,
        consumed_at__isnull=True,
        expires_at__gt=now,
    ).update(consumed_at=now)
    return EmployeeAccessToken.issue(employee, enrollment=enrollment)


def deliver_access_code(employee, raw_token, code, allow_console=True):
    subject, body = access_email(employee, raw_token, code)
    return _deliver(
        "access", employee, subject, body, allow_console=allow_console
    )


def issue_access_token(enrollment):
    """Issue a fresh single-use token for the enrollment and email it.

    Returns ``(raw_token, code)`` for the caller to deliver, or ``(None, None)``
    if the employee has no email (token is still issued; delivery is skipped).
    """
    employee = enrollment.employee
    _, raw_token, code = EmployeeAccessToken.issue(employee, enrollment=enrollment)
    deliver_access_code(employee, raw_token, code)
    return raw_token, code


def resend_access_token(enrollment):
    """Idempotent resend (spec secure-access §Token Delivery).

    Any previously unconsumed, unexpired token for this enrollment is invalidated
    (marked consumed) so exactly ONE active token exists, then a fresh token is
    issued and emailed. Repeated resends simply rotate the active token rather
    than leaving multiple valid links in the wild.
    """
    employee = enrollment.employee
    _, raw_token, code = rotate_employee_access(employee, enrollment=enrollment)
    deliver_access_code(employee, raw_token, code)
    return raw_token, code


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

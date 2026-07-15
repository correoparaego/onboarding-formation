"""Tests for secure-access issuance + delivery logging (spec secure-access, notifications)."""
from django.contrib.auth import get_user_model
from django.test import TestCase

from authentication.models import EmployeeAccessToken
from courses.models import Course
from employees.models import Employee
from notifications import services
from notifications.models import NotificationLog
from notifications.transports import get_transport
from reading_gate.models import Enrollment

User = get_user_model()


def _make_enrollment():
    emp = Employee.objects.create(
        dni="12345678Z", name="Juan", position="X", email="juan@empresa.com"
    )
    course = Course.objects.create(title="A")
    return (
        Enrollment.objects.create(employee=emp, course=course, status="assigned"),
        emp,
    )


class TransportConfigTests(TestCase):
    def test_default_transport_is_console(self):
        self.assertEqual(get_transport().name, "console")


class IssuanceTests(TestCase):
    def test_issue_creates_token_and_logs_without_raw_secret(self):
        enr, emp = _make_enrollment()
        raw_token, code = services.issue_access_token(enr)
        self.assertIsNotNone(raw_token)
        # A single-use token row exists (only hashes stored).
        self.assertEqual(
            EmployeeAccessToken.objects.filter(employee=emp, enrollment=enr).count(), 1
        )
        log = NotificationLog.objects.filter(template="access").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.recipient, emp.email)
        self.assertEqual(log.status, "sent")
        # Raw token/code must NEVER appear in the log.
        self.assertNotIn(raw_token, log.detail)
        self.assertNotIn(raw_token, log.recipient)
        self.assertNotIn(code, log.detail)

    def test_resend_is_idempotent_single_active_token(self):
        enr, emp = _make_enrollment()
        services.resend_access_token(enr)
        services.resend_access_token(enr)
        # Only ONE unconsumed token remains (old ones invalidated on resend).
        active = EmployeeAccessToken.objects.filter(
            employee=emp, enrollment=enr, consumed_at__isnull=True
        ).count()
        self.assertEqual(active, 1)
        # Two delivery logs recorded (best-effort delivery each time).
        self.assertEqual(
            NotificationLog.objects.filter(
                template="access", recipient=emp.email
            ).count(),
            2,
        )

    def test_no_email_skips_delivery(self):
        emp = Employee.objects.create(
            dni="22222222A", name="Nil", position="X", email=""
        )
        course = Course.objects.create(title="A")
        enr = Enrollment.objects.create(
            employee=emp, course=course, status="assigned"
        )
        raw_token, code = services.issue_access_token(enr)
        self.assertIsNotNone(raw_token)
        log = NotificationLog.objects.filter(template="access").first()
        self.assertEqual(log.status, "skipped")


class ResendEndpointTests(TestCase):
    def test_admin_resend_returns_ok_without_echoing_token(self):
        from notifications.views import admin_resend_access

        emp = Employee.objects.create(
            dni="77777777F", name="Ona", position="X", email="ona@e.com"
        )
        course = Course.objects.create(title="A")
        enr = Enrollment.objects.create(
            employee=emp, course=course, status="assigned"
        )
        admin = User.objects.create_user("adm", "adm@x.com", "pw", is_staff=True)
        self.client.force_login(admin)
        resp = self.client.post(f"/api/admin/enrollment/{enr.id}/resend-access")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["employee"], "Ona")
        # Raw token/code must not leak into the API response.
        self.assertNotIn("token", body)
        self.assertNotIn("code", body)

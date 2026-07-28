"""Tests for secure-access issuance + delivery logging (spec secure-access, notifications)."""
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from authentication.models import EmployeeAccessToken
from courses.models import Course
from employees.models import Employee
from notifications import services
from notifications.models import NotificationLog
from notifications.transports import get_transport
from reading_gate.models import AuditEvent, Enrollment

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


class BatchAccessCodeTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "batch-admin", "batch-admin@example.com", "pw", is_staff=True
        )
        self.course = Course.objects.create(title="Batch")
        self.employees = [
            Employee.objects.create(
                dni=f"1234567{index}Z",
                name=f"Empleado {index}",
                position="X",
                email=f"employee{index}@example.com",
            )
            for index in range(2)
        ]
        for employee in self.employees:
            Enrollment.objects.create(
                employee=employee, course=self.course, status="assigned"
            )
        self.client.force_login(self.admin)

    def test_batch_returns_unique_codes_once_and_invalidates_old_access(self):
        old_row, _, old_code = EmployeeAccessToken.issue(self.employees[0])
        response = self.client.post(
            "/api/admin/access-codes/batch",
            data={"employee_ids": [self.employees[0].id, self.employees[0].id, self.employees[1].id]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        results = response.json()["results"]
        self.assertEqual(response["Cache-Control"], "no-store, private")
        self.assertEqual(len(results), 2)
        codes = [result["code"] for result in results]
        self.assertEqual(len(set(codes)), 2)
        self.assertTrue(all(len(code) == 8 for code in codes))
        old_row.refresh_from_db()
        self.assertIsNotNone(old_row.consumed_at)
        self.assertEqual(EmployeeAccessToken.redeem(old_code)[1], "consumed")

        persisted = json.dumps(
            list(NotificationLog.objects.values("recipient", "detail"))
            + list(AuditEvent.objects.values("payload"))
        )
        for code in codes:
            self.assertNotIn(code, persisted)
        audit = AuditEvent.objects.filter(event_type="employee_access_rotated").first()
        self.assertEqual(audit.payload["actor_id"], self.admin.id)

    @override_settings(EMAIL_TRANSPORT="resend", RESEND_API_KEY="")
    def test_delivery_failure_keeps_code_available(self):
        response = self.client.post(
            "/api/admin/access-codes/batch",
            data={"employee_ids": [self.employees[0].id]},
            content_type="application/json",
        )
        result = response.json()["results"][0]
        self.assertEqual(result["delivery_status"], "failed")
        employee, status = EmployeeAccessToken.redeem(result["code"])
        self.assertEqual(status, "ok")
        self.assertEqual(employee, self.employees[0])

    def test_batch_limit_is_enforced(self):
        response = self.client.post(
            "/api/admin/access-codes/batch",
            data={"employee_ids": list(range(1, 102))},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_batch_endpoint_requires_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        denied = csrf_client.post(
            "/api/admin/access-codes/batch",
            data={"employee_ids": [self.employees[0].id]},
            content_type="application/json",
        )
        self.assertEqual(denied.status_code, 403)

    def test_missing_employees_and_non_object_json_are_reported(self):
        missing_id = 999999
        response = self.client.post(
            "/api/admin/access-codes/batch",
            data={"employee_ids": [self.employees[0].id, missing_id]},
            content_type="application/json",
        )
        self.assertEqual(response.json()["missing_employee_ids"], [missing_id])
        invalid = self.client.post(
            "/api/admin/access-codes/batch",
            data=[self.employees[0].id],
            content_type="application/json",
        )
        self.assertEqual(invalid.status_code, 400)

    @patch("notifications.views.reading_services.audit_event", side_effect=RuntimeError("audit down"))
    def test_audit_failure_does_not_hide_committed_code(self, _audit):
        response = self.client.post(
            "/api/admin/access-codes/batch",
            data={"employee_ids": [self.employees[0].id]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        code = response.json()["results"][0]["code"]
        self.assertEqual(EmployeeAccessToken.redeem(code)[1], "ok")

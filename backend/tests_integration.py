"""Top-level integration happy-path (spec audit-log, design §Testing).

Exercises the full compliance flow through the real HTTP API:
  import (admin) -> read gate (employee heartbeat) -> comprehension test
  (employee submit) -> certificate (admin) -> audit trail (admin read).
"""
import io

from django.test import TestCase

import pandas as pd

from courses.models import Course, Position, Question, QuestionBank, Section
from employees.models import Employee
from reading_gate import services
from reading_gate.models import AuditEvent, Enrollment


class HappyPathIntegrationTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.admin = User.objects.create_user(
            "admin", "admin@x.com", "pw", is_staff=True
        )
        self.pos = Position.objects.create(name="Operario")
        self.course = Course.objects.create(title="A", min_time_divisor=3)
        self.pos.courses.add(self.course)
        for i in range(1, 3):  # 2 sections, base 30 -> minTime 10
            Section.objects.create(course=self.course, order=i, section_base=30)
        bank = QuestionBank.objects.create(course=self.course)
        for i in range(8):
            Question.objects.create(
                bank=bank, text=f"Q{i}", options=["yes", "no"], correct_index=0
            )

    def _import_employee(self):
        df = pd.DataFrame(
            [
                {
                    "dni": "12345678Z",
                    "name": "Juan Perez",
                    "position": "Operario",
                    "email": "juan@empresa.com",
                }
            ]
        )
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        self.client.force_login(self.admin)
        resp = self.client.post(
            "/api/import", data={"file": buf}, format="multipart"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["created"], 1)
        self.assertGreaterEqual(body["enrollments_created"], 1)

    def _employee_session(self, emp):
        # Drop any admin session first so the employee-only route middleware
        # does not reject the request (admin->employee is 403 by design).
        self.client.logout()
        session = self.client.session
        session["employee_id"] = emp.id
        session.save()

    def _read_to_complete(self, enr):
        for section in self.course.sections.order_by("order"):
            resp = self.client.post(
                "/api/reading/heartbeat",
                data={
                    "enrollment_id": enr.id,
                    "section_order": section.order,
                    "delta": 30,
                    "visibility": True,
                    "interaction": True,
                    "device_id": "dev-1",
                    "session_id": "sess-1",
                },
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 200)

    def test_import_read_test_cert_audit(self):
        self._import_employee()
        emp = Employee.objects.get(email="juan@empresa.com")
        enr = Enrollment.objects.get(employee=emp, course=self.course)

        # Employee reads the course to completion (server gating).
        self._employee_session(emp)
        self._read_to_complete(enr)

        # Fetch the test (correct_index withheld by the API).
        q_resp = self.client.get(f"/api/test/questions?enrollment_id={enr.id}")
        self.assertEqual(q_resp.status_code, 200)

        # Build the correct answers from the deterministic subset.
        subset = services.get_test_subset(enr, 1)
        answers = [
            {"question_id": q.id, "selected_index": q.correct_index} for q in subset
        ]
        s_resp = self.client.post(
            "/api/test/submit",
            data={"enrollment_id": enr.id, "answers": answers},
            content_type="application/json",
        )
        self.assertEqual(s_resp.status_code, 200)
        self.assertEqual(s_resp.json()["result"], "pass")

        # Admin fetches the certificate PDF.
        self.client.logout()
        self.client.force_login(self.admin)
        # Ensure no employee session lingers.
        session = self.client.session
        session.pop("employee_id", None)
        session.save()
        c_resp = self.client.get(f"/api/certificate/{enr.id}")
        self.assertEqual(c_resp.status_code, 200)
        self.assertEqual(c_resp["Content-Type"], "application/pdf")

        # Audit trail: append-only read API returns the issuance event.
        a_resp = self.client.get(
            f"/api/audit?enrollment={enr.id}&event_type=certificate_issued"
        )
        self.assertEqual(a_resp.status_code, 200)
        self.assertGreaterEqual(a_resp.json()["count"], 1)

        # Cross-check the broader coverage via direct queries.
        self.assertGreaterEqual(
            AuditEvent.objects.filter(event_type="import").count(), 1
        )
        self.assertGreaterEqual(
            AuditEvent.objects.filter(event_type="enrollment_assigned").count(), 1
        )
        self.assertEqual(
            AuditEvent.objects.filter(event_type="section_complete").count(), 2
        )
        self.assertEqual(
            AuditEvent.objects.filter(event_type="section_unlock").count(), 1
        )
        self.assertGreaterEqual(
            AuditEvent.objects.filter(event_type="attempt_submit").count(), 1
        )
        # No DNI / token leakage in any audit payload.
        for ev in AuditEvent.objects.all():
            self.assertNotIn("dni", (ev.payload or {}))

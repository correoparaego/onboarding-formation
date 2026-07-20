"""Audit API contract + coverage tests (spec audit-log).

- Append-only: no create/update/delete endpoint; non-GET -> 405.
- Read/filter by enrollment / employee / event_type / date.
- No DNI / token / PII in payloads.
- Coverage: import, enrollment_assigned, section_unlock, certificate_issued.
"""
import io

from django.contrib.auth import get_user_model
from django.test import TestCase

import pandas as pd

from courses.models import Course, Position, Question, QuestionBank, Section
from employees.models import Employee
from reading_gate import services
from reading_gate.models import AuditEvent, Enrollment

User = get_user_model()


def _seed(enrollment, event_type, n=1, payload=None):
    payload = payload or {}
    for _ in range(n):
        AuditEvent.objects.create(
            enrollment=enrollment, event_type=event_type, payload=payload
        )


class AuditApiTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("a", "a@x.com", "pw", is_staff=True)
        self.emp = Employee.objects.create(
            dni="12345678Z", name="Juan", position="X", email="j@e.com"
        )
        self.course = Course.objects.create(title="A", min_time_divisor=3)
        self.enr = Enrollment.objects.create(
            employee=self.emp, course=self.course, status="complete"
        )
        _seed(self.enr, "section_complete", 2)

    def test_post_is_rejected(self):
        self.client.force_login(self.admin)
        resp = self.client.post("/api/audit", data={}, content_type="application/json")
        self.assertEqual(resp.status_code, 405)

    def test_put_and_delete_rejected(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.put("/api/audit").status_code, 405)
        self.assertEqual(self.client.delete("/api/audit").status_code, 405)

    def test_get_filters_by_event_type(self):
        self.client.force_login(self.admin)
        resp = self.client.get("/api/audit?event_type=section_complete")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 2)

    def test_get_filters_by_enrollment(self):
        self.client.force_login(self.admin)
        resp = self.client.get(f"/api/audit?enrollment={self.enr.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 2)

    def test_get_filters_by_employee(self):
        self.client.force_login(self.admin)
        resp = self.client.get(f"/api/audit?employee={self.emp.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 2)

    def test_get_filters_by_date(self):
        self.client.force_login(self.admin)
        from django.utils import timezone

        today = self.enr.audit_events.first().timestamp.date().isoformat()
        resp = self.client.get(f"/api/audit?date={today}")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.json()["count"], 2)

    def test_no_dni_in_payloads(self):
        self.client.force_login(self.admin)
        resp = self.client.get("/api/audit")
        body = resp.json()
        for row in body["results"]:
            self.assertNotIn("dni", row)
            self.assertNotIn("dni", (row.get("payload") or {}))

    def test_pagination_cap(self):
        _seed(self.enr, "section_complete", 501)
        self.client.force_login(self.admin)
        resp = self.client.get("/api/audit?event_type=section_complete")
        self.assertEqual(resp.json()["count"], 500)


class AuditCoverageTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("a2", "a2@x.com", "pw", is_staff=True)
        self.pos = Position.objects.create(name="Operario")
        self.course = Course.objects.create(title="A", min_time_divisor=3)
        self.pos.courses.add(self.course)
        for i in range(1, 3):
            Section.objects.create(course=self.course, order=i, section_base=30)
        bank = QuestionBank.objects.create(course=self.course)
        for i in range(8):
            Question.objects.create(
                bank=bank, text=f"Q{i}", options=["yes", "no"], correct_index=0
            )

    def _import(self):
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
        return self.client.post(
            "/api/import", data={"file": buf}, format="multipart"
        )

    def test_import_emits_import_and_enrollment_assigned(self):
        resp = self._import()
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(
            AuditEvent.objects.filter(event_type="import").count(), 1
        )
        self.assertGreaterEqual(
            AuditEvent.objects.filter(event_type="enrollment_assigned").count(), 1
        )

    def test_heartbeat_emits_section_unlock(self):
        emp = Employee.objects.create(
            dni="22222222A", name="Luz", position="Operario", email="luz@e.com"
        )
        enr = Enrollment.objects.create(
            employee=emp, course=self.course, status="assigned"
        )
        for section in self.course.sections.order_by("order"):
            services.process_heartbeat(
                enr,
                section_order=section.order,
                delta=30,
                visibility=True,
                interaction=True,
            )
        self.assertEqual(
            AuditEvent.objects.filter(event_type="section_complete").count(), 2
        )
        self.assertEqual(
            AuditEvent.objects.filter(event_type="section_unlock").count(), 1
        )

    def test_certificate_issued_event(self):
        emp = Employee.objects.create(
            dni="33333333B", name="Sol", position="Operario", email="sol@e.com"
        )
        enr = Enrollment.objects.create(
            employee=emp, course=self.course, status="complete"
        )
        subset = services.get_test_subset(enr, 1)
        answers = [
            {"question_id": q.id, "selected_index": q.correct_index} for q in subset
        ]
        services.grade_submission(enr, answers)
        self.assertEqual(enr.status, "passed")
        self.client.force_login(self.admin)
        resp = self.client.get(f"/api/certificate/{enr.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(
            AuditEvent.objects.filter(event_type="certificate_issued").count(), 1
        )

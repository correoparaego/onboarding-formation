"""Tests for enrollment-assignment (spec enrollment-assignment, Phase 7)."""
import io

from django.contrib.auth import get_user_model
from django.test import TestCase

import pandas as pd

from courses.models import Course, Position
from employees.models import Employee
from reading_gate.models import Enrollment
from reading_gate.services import assign_mandatory_courses

User = get_user_model()


class EnrollmentAssignmentTests(TestCase):
    def setUp(self):
        self.pos = Position.objects.create(name="Operario")
        self.course_a = Course.objects.create(title="A")
        self.course_b = Course.objects.create(title="B")
        self.pos.courses.set([self.course_a, self.course_b])

    def test_auto_assign_on_import_is_idempotent(self):
        admin = User.objects.create_user("a", "a@x.com", "pw", is_staff=True)
        self.client.force_login(admin)

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

        resp = self.client.post(
            "/api/import", data={"file": buf}, format="multipart"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["created"], 1)
        self.assertEqual(body["enrollments_created"], 2)  # A and B
        self.assertEqual(Enrollment.objects.count(), 2)

        # Re-import the SAME employee -> no duplicate enrollment.
        df2 = pd.DataFrame(
            [
                {
                    "dni": "12345678Z",
                    "name": "Juan Perez",
                    "position": "Operario",
                    "email": "juan@empresa.com",
                }
            ]
        )
        buf2 = io.BytesIO()
        df2.to_excel(buf2, index=False)
        buf2.seek(0)
        resp2 = self.client.post(
            "/api/import", data={"file": buf2}, format="multipart"
        )
        self.assertEqual(resp2.json()["duplicates"], 1)
        self.assertEqual(resp2.json()["enrollments_created"], 0)
        self.assertEqual(Enrollment.objects.count(), 2)  # unchanged

    def test_assign_service_idempotent_directly(self):
        emp = Employee.objects.create(
            dni="87654321X",
            name="Ana",
            position="Operario",
            email="ana@empresa.com",
        )
        n1 = assign_mandatory_courses(emp)
        self.assertEqual(n1, 2)
        n2 = assign_mandatory_courses(emp)
        self.assertEqual(n2, 0)
        self.assertEqual(Enrollment.objects.filter(employee=emp).count(), 2)

    def test_no_position_match_creates_no_enrollment(self):
        emp = Employee.objects.create(
            dni="11111111H",
            name="Bob",
            position="Gerente",
            email="bob@empresa.com",
        )
        self.assertEqual(assign_mandatory_courses(emp), 0)
        self.assertEqual(Enrollment.objects.filter(employee=emp).count(), 0)


# ---------------------------------------------------------------------------
# Timed reading gate + comprehension test (spec timed-reading, comprehension-test)
# ---------------------------------------------------------------------------
import json  # noqa: E402

from courses.models import Course, Question, QuestionBank, Section  # noqa: E402
from reading_gate import services  # noqa: E402
from reading_gate.models import AuditEvent, Enrollment, ReadingProgress  # noqa: E402


def _make_course_with_bank(num_sections=2, section_base=90, num_questions=8):
    """Build a course (divisor 3 -> minTime 30/s), sections, and a question bank."""
    course = Course.objects.create(title="GateCourse", min_time_divisor=3)
    for i in range(1, num_sections + 1):
        Section.objects.create(course=course, order=i, section_base=section_base)
    bank = QuestionBank.objects.create(course=course)
    for i in range(num_questions):
        Question.objects.create(
            bank=bank,
            text=f"Q{i}",
            options=["yes", "no"],
            correct_index=0,
        )
    return course


def _make_enrollment(course, employee, status="assigned"):
    return Enrollment.objects.create(
        employee=employee, course=course, status=status
    )


class ReadingGateTests(TestCase):
    def setUp(self):
        self.emp = Employee.objects.create(
            dni="22222222A", name="Luz", position="X", email="luz@e.com"
        )
        self.course = _make_course_with_bank(num_sections=2, section_base=90)
        self.enr = _make_enrollment(self.course, self.emp)

    def test_section_unlocks_only_when_previous_complete(self):
        # Heartbeat section 2 BEFORE section 1 is done -> locked.
        r = services.process_heartbeat(
            self.enr, section_order=2, delta=30, visibility=True, interaction=True
        )
        self.assertTrue(r["locked"])
        self.assertEqual(ReadingProgress.objects.count(), 0)

        # Complete section 1.
        r1 = services.process_heartbeat(
            self.enr, section_order=1, delta=30, visibility=True, interaction=True
        )
        self.assertTrue(r1["section_complete"])
        self.assertFalse(r1["locked"])

        # Now section 2 is reachable.
        r2 = services.process_heartbeat(
            self.enr, section_order=2, delta=30, visibility=True, interaction=True
        )
        self.assertFalse(r2["locked"])
        self.assertTrue(r2["all_sections_complete"])
        self.assertEqual(r2["enrollment_status"], "complete")
        self.assertTrue(r2["test_unlocked"])
        # audit: section_complete + reading_complete
        self.assertEqual(
            AuditEvent.objects.filter(event_type="section_complete").count(), 2
        )
        self.assertEqual(
            AuditEvent.objects.filter(event_type="reading_complete").count(), 1
        )

    def test_visibility_and_interaction_required_to_credit(self):
        r = services.process_heartbeat(
            self.enr, section_order=1, delta=30, visibility=False, interaction=True
        )
        self.assertEqual(r["credited"], 0)
        self.assertFalse(r["section_complete"])

        r2 = services.process_heartbeat(
            self.enr, section_order=1, delta=30, visibility=True, interaction=True
        )
        self.assertEqual(r2["credited"], 30)
        self.assertTrue(r2["section_complete"])

    def test_delta_is_clamped(self):
        r = services.process_heartbeat(
            self.enr, section_order=1, delta=100000, visibility=True, interaction=True
        )
        self.assertEqual(r["credited"], services.MAX_HEARTBEAT_DELTA)
        self.assertEqual(r["accumulated"], services.MAX_HEARTBEAT_DELTA)

    def test_negative_delta_is_ignored(self):
        r = services.process_heartbeat(
            self.enr, section_order=1, delta=-50, visibility=True, interaction=True
        )
        self.assertEqual(r["credited"], 0)
        self.assertEqual(r["accumulated"], 0)


class ComprehensionTestTests(TestCase):
    def setUp(self):
        self.emp = Employee.objects.create(
            dni="33333333B", name="Sol", position="Y", email="sol@e.com"
        )
        self.course = _make_course_with_bank(num_sections=1, num_questions=8)
        self.enr = _make_enrollment(self.course, self.emp, status="complete")

    def _correct_answers(self, attempt_no=1):
        subset = services.get_test_subset(self.enr, attempt_no)
        return [{"question_id": q.id, "selected_index": q.correct_index} for q in subset]

    def test_subset_is_deterministic_and_distinct(self):
        a1 = [q.id for q in services.get_test_subset(self.enr, 1)]
        a1b = [q.id for q in services.get_test_subset(self.enr, 1)]
        a2 = [q.id for q in services.get_test_subset(self.enr, 2)]
        self.assertEqual(a1, a1b)  # deterministic
        self.assertNotEqual(a1, a2)  # distinct per attempt

    def test_pass_flow_sets_passed(self):
        res = services.grade_submission(self.enr, self._correct_answers(1))
        self.assertEqual(res["result"], "pass")
        self.assertEqual(res["enrollment_status"], "passed")
        self.assertEqual(res["attempts_used"], 1)
        self.assertEqual(
            AuditEvent.objects.filter(event_type="attempt_submit").count(), 1
        )

    def test_fail_resets_reading_and_increments(self):
        # Give the employee some reading progress first.
        s1 = self.course.sections.first()
        ReadingProgress.objects.create(
            enrollment=self.enr, section=s1, accumulated_time=30
        )
        wrong = [{"question_id": q.id, "selected_index": 1 - q.correct_index}
                 for q in services.get_test_subset(self.enr, 1)]
        res = services.grade_submission(self.enr, wrong)
        self.assertEqual(res["result"], "fail")
        self.assertEqual(res["attempts_used"], 1)
        self.assertEqual(res["enrollment_status"], "in_progress")
        self.assertTrue(res["reading_reset"])
        self.assertEqual(ReadingProgress.objects.filter(enrollment=self.enr).count(), 0)
        self.assertEqual(
            AuditEvent.objects.filter(event_type="attempt_fail").count(), 1
        )

    def test_fourth_attempt_is_blocked_and_exhausted(self):
        self.enr.attempts_used = 3
        self.enr.save()
        res = services.grade_submission(self.enr, self._correct_answers(4))
        self.assertEqual(res["status_code"], 409)
        self.assertEqual(res["enrollment_status"], "failed_exhausted")
        self.assertEqual(
            AuditEvent.objects.filter(event_type="attempt_blocked").count(), 1
        )

    def test_get_questions_withholds_correct_index(self):
        payload = services.get_test_questions(self.enr)
        self.assertEqual(payload["status_code"], 200)
        for q in payload["questions"]:
            self.assertNotIn("correct_index", q)
        self.assertEqual(
            AuditEvent.objects.filter(event_type="attempt_start").count(), 1
        )


class ReadingGateAuthzTests(TestCase):
    def setUp(self):
        self.emp = Employee.objects.create(
            dni="44444444C", name="Mar", position="Z", email="mar@e.com"
        )
        self.other = Employee.objects.create(
            dni="55555555D", name="Nil", position="Z", email="nil@e.com"
        )
        self.course = _make_course_with_bank(num_sections=1, section_base=30)
        self.enr = _make_enrollment(self.course, self.emp)

    def _emp_session(self, emp):
        session = self.client.session
        session["employee_id"] = emp.id
        session.save()

    def test_heartbeat_requires_employee_session(self):
        resp = self.client.post(
            "/api/reading/heartbeat",
            data=json.dumps({"enrollment_id": self.enr.id, "section_order": 1,
                             "delta": 30, "visibility": True, "interaction": True}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_employee_cannot_act_on_others_enrollment(self):
        self._emp_session(self.other)
        resp = self.client.post(
            "/api/reading/heartbeat",
            data=json.dumps({"enrollment_id": self.enr.id, "section_order": 1,
                             "delta": 30, "visibility": True, "interaction": True}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_employee_heartbeat_accumulates(self):
        self._emp_session(self.emp)
        resp = self.client.post(
            "/api/reading/heartbeat",
            data=json.dumps({"enrollment_id": self.enr.id, "section_order": 1,
                              "delta": 30, "visibility": True, "interaction": True}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["accumulated"], 30)
        self.assertTrue(body["section_complete"])


# ---------------------------------------------------------------------------
# PR5 — Expediente persistence + badge award on pass (spec expediente, badges)
# ---------------------------------------------------------------------------
from certificates.models import Badge, EmployeeBadge  # noqa: E402
from reading_gate.models import Expediente  # noqa: E402


class ExpedienteAndBadgesTests(TestCase):
    def setUp(self):
        self.emp = Employee.objects.create(
            dni="66666666E", name="Eli", position="Y", email="eli@e.com"
        )
        self.course = _make_course_with_bank(num_sections=1, num_questions=8)
        self.enr = _make_enrollment(self.course, self.emp, status="complete")

    def _correct_answers(self, attempt_no=1):
        subset = services.get_test_subset(self.enr, attempt_no)
        return [
            {"question_id": q.id, "selected_index": q.correct_index} for q in subset
        ]

    def test_pass_writes_expediente_and_awards_first_badges(self):
        res = services.grade_submission(self.enr, self._correct_answers(1))
        self.assertEqual(res["result"], "pass")
        exp = Expediente.objects.get(enrollment=self.enr)
        self.assertEqual(exp.status, "passed")
        self.assertEqual(exp.attempts_used, 1)
        self.assertEqual(exp.score, res["score"])
        self.assertEqual(exp.total, res["total"])
        self.assertIsNotNone(exp.completed_at)
        # First pass + first attempt -> primer-curso + sin-fallos.
        slugs = set(
            EmployeeBadge.objects.filter(employee=self.emp).values_list(
                "badge__slug", flat=True
            )
        )
        self.assertIn("primer-curso", slugs)
        self.assertIn("sin-fallos", slugs)

    def test_expediente_admin_filter(self):
        services.grade_submission(self.enr, self._correct_answers(1))
        admin = User.objects.create_user("adm", "adm@x.com", "pw", is_staff=True)
        self.client.force_login(admin)
        resp = self.client.get(
            f"/api/expediente?course={self.course.id}&status=passed"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        # A status that does not match -> 0 results.
        resp2 = self.client.get(
            f"/api/expediente?course={self.course.id}&status=assigned"
        )
        self.assertEqual(resp2.json()["count"], 0)

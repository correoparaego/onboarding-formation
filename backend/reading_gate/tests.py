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

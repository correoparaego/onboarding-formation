"""Tests for certificate PDF + badge award (spec certificate, badges)."""
import io

from django.contrib.auth import get_user_model
from django.test import TestCase
from PyPDF2 import PdfReader

from certificates import services
from certificates.models import Badge, Certificate, EmployeeBadge
from courses.models import Course, Question, QuestionBank, Section
from employees.models import Employee
from reading_gate.models import Enrollment, Expediente

User = get_user_model()


def _pdf_text(pdf_bytes):
    # The PDF content stream is compressed; extract rendered text to verify it.
    return PdfReader(io.BytesIO(pdf_bytes)).pages[0].extract_text() or ""


def _build_passed_enrollment(dni="12345678Z", name="Juan Perez"):
    emp = Employee.objects.create(
        dni=dni, name=name, position="X", email="j@e.com"
    )
    course = Course.objects.create(title="Curso A", min_time_divisor=3)
    Section.objects.create(course=course, order=1, section_base=90)
    bank = QuestionBank.objects.create(course=course)
    Question.objects.create(bank=bank, text="Q", options=["a", "b"], correct_index=0)
    enr = Enrollment.objects.create(
        employee=emp, course=course, status="passed", attempts_used=1
    )
    Expediente.objects.create(
        enrollment=enr,
        employee=emp,
        course=course,
        status="passed",
        attempts_used=1,
        score=1,
        total=1,
    )
    return enr


class BadgeSeedTests(TestCase):
    def test_initial_badges_seeded(self):
        services.ensure_badges()
        slugs = set(Badge.objects.values_list("slug", flat=True))
        self.assertEqual(slugs, {"primer-curso", "catalogo-completo", "sin-fallos"})


class CertificatePdfTests(TestCase):
    def test_pdf_contains_verbatim_dni_and_title(self):
        enr = _build_passed_enrollment(dni="12345678Z")
        pdf, _ = services.generate_certificate_pdf(enr)
        self.assertTrue(pdf.startswith(b"%PDF"))
        text = _pdf_text(pdf)
        self.assertIn("12345678Z", text)  # DNI verbatim
        self.assertIn("Curso A", text)  # course title
        self.assertIn("apto", text)  # evaluation

    def test_one_certificate_per_enrollment_and_idempotent_hash(self):
        enr = _build_passed_enrollment()
        cert, _ = Certificate.objects.get_or_create(enrollment=enr)
        _, hash1 = services.generate_certificate_pdf(enr, issued_at=cert.issued_at)
        _, hash2 = services.generate_certificate_pdf(enr, issued_at=cert.issued_at)
        self.assertEqual(hash1, hash2)  # regeneration reproduces core fields
        self.assertEqual(Certificate.objects.filter(enrollment=enr).count(), 1)

    def test_certificate_view_requires_passed_and_is_pdf(self):
        enr = _build_passed_enrollment(dni="12345678Z")
        admin = User.objects.create_user("adm", "adm@x.com", "pw", is_staff=True)
        self.client.force_login(admin)
        resp = self.client.get(f"/api/certificate/{enr.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertIn("12345678Z", _pdf_text(resp.content))
        # Non-passed enrollment -> 409.
        enr2 = _build_passed_enrollment(dni="99999999R", name="Noa")
        enr2.status = "assigned"
        enr2.save()
        resp2 = self.client.get(f"/api/certificate/{enr2.id}")
        self.assertEqual(resp2.status_code, 409)

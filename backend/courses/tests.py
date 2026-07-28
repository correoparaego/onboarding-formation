"""Tests for course-management (spec course-management, Phase 5)."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Course, CourseVersion, Position, QuestionBank, Section

User = get_user_model()


class CourseManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "a", "a@x.com", "pw", is_staff=True
        )
        self.pos = Position.objects.create(name="Operario")
        self.course = Course.objects.create(title="Seguridad")
        self.course.position_catalog.add(self.pos)

    def test_catalog_lookup_returns_mandatory_courses(self):
        c = self.client
        c.force_login(self.admin)
        resp = c.get("/api/courses/catalog/", {"position": "Operario"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["position"], "Operario")
        self.assertEqual(len(body["courses"]), 1)
        self.assertEqual(body["courses"][0]["id"], self.course.id)

    def test_catalog_case_insensitive(self):
        c = self.client
        c.force_login(self.admin)
        resp = c.get("/api/courses/catalog/", {"position": "operario"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["courses"]), 1)

    def test_course_create_with_sections(self):
        c = self.client
        c.force_login(self.admin)
        resp = c.post(
            "/api/courses/",
            data={
                "title": "Nuevo",
                "sections": "[{\"order\": 1, \"section_base\": 90}]",
                "position_ids": [self.pos.id],
            },
        )
        self.assertEqual(resp.status_code, 201)
        new = Course.objects.get(title="Nuevo")
        self.assertEqual(new.sections.count(), 1)
        self.assertTrue(new.position_catalog.filter(id=self.pos.id).exists())

    def test_single_correct_enforced_on_save(self):
        c = self.client
        c.force_login(self.admin)
        # correct_index out of range -> rejected.
        resp = c.post(
            "/api/banks/",
            data={
                "course_id": self.course.id,
                "questions": [
                    {"text": "q", "options": ["a", "b"], "correct_index": 5}
                ],
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(QuestionBank.objects.filter(course=self.course).count(), 0)


class CourseVersioningTests(TestCase):
    def test_publishing_new_version_preserves_previous_content(self):
        course = Course.objects.create(title="Seguridad")
        first = CourseVersion.objects.create(
            course=course,
            number=1,
            title=course.title,
            status="published",
            published_at=timezone.now(),
        )
        course.active_version = first
        course.save(update_fields=["active_version"])
        Section.objects.create(
            course=course,
            version=first,
            order=1,
            title="Original",
            content="Contenido inicial",
            section_base=90,
        )
        draft = CourseVersion.objects.create(
            course=course, number=2, title=course.title
        )
        Section.objects.create(
            course=course,
            version=draft,
            order=1,
            title="Original",
            content="Contenido revisado",
            section_base=90,
        )

        self.assertEqual(
            first.sections.get(order=1).content, "Contenido inicial"
        )
        self.assertEqual(
            draft.sections.get(order=1).content,
            "Contenido revisado",
        )
        self.assertEqual(CourseVersion.objects.filter(course=course).count(), 2)

"""Tests for course-management (spec course-management, Phase 5)."""
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.utils import timezone

from .models import Course, CourseVersion, Position, QuestionBank, Section
from .services import create_course, create_draft_version

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
        self.assertEqual(new.active_version.number, 1)
        self.assertEqual(new.active_version.status, "published")
        self.assertEqual(new.sections.first().version, new.active_version)
        self.assertTrue(new.position_catalog.filter(id=self.pos.id).exists())

    def test_draft_can_be_edited_and_published_without_changing_version_one(self):
        self.client.force_login(self.admin)
        _, first = create_course(
            "Versionado",
            sections=[{"order": 1, "title": "Uno", "content": "Original"}],
        )
        draft_resp = self.client.post(f"/api/courses/{first.course_id}/draft/")
        draft = draft_resp.json()["version"]
        update = self.client.patch(
            f"/api/course-versions/{draft['id']}/",
            data={
                "title": "Versionado 2",
                "sections": [
                    {"order": 1, "title": "Uno", "content": "Revisado"}
                ],
            },
            content_type="application/json",
        )
        self.assertEqual(update.status_code, 200)
        publish = self.client.post(
            f"/api/course-versions/{draft['id']}/publish/"
        )
        self.assertEqual(publish.status_code, 200)
        first.refresh_from_db()
        self.assertEqual(first.sections.get().content, "Original")

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

    def test_admin_can_upload_valid_pdf_to_editable_section(self):
        admin = User.objects.create_user("pdf", "pdf@example.com", "pw", is_staff=True)
        course, version = create_course(
            "PDF", sections=[{"order": 1, "title": "Lectura"}]
        )
        section = version.sections.get()
        self.client.force_login(admin)
        upload = SimpleUploadedFile(
            "section.pdf", b"%PDF-1.4\ncontent", content_type="application/pdf"
        )
        with tempfile.TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            response = self.client.post(
                f"/api/sections/{section.id}/pdf/", {"pdf": upload}
            )
            self.assertEqual(response.status_code, 200)
            download = self.client.get(f"/api/sections/{section.id}/pdf/")
            self.assertEqual(download.status_code, 200)
            self.assertEqual(download["Content-Type"], "application/pdf")
            download.close()

    def test_section_rejects_non_pdf_content(self):
        admin = User.objects.create_user("badpdf", "bad@example.com", "pw", is_staff=True)
        _, version = create_course(
            "PDF inválido", sections=[{"order": 1, "title": "Lectura"}]
        )
        self.client.force_login(admin)
        response = self.client.post(
            f"/api/sections/{version.sections.get().id}/pdf/",
            {
                "pdf": SimpleUploadedFile(
                    "fake.pdf", b"not-a-pdf", content_type="application/pdf"
                )
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_draft_pdf_is_independent_from_published_version(self):
        admin = User.objects.create_user("copy", "copy@example.com", "pw", is_staff=True)
        course, published = create_course(
            "Copias", sections=[{"order": 1, "title": "Lectura"}]
        )
        self.client.force_login(admin)
        with tempfile.TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            original = published.sections.get()
            self.client.post(
                f"/api/sections/{original.id}/pdf/",
                {"pdf": SimpleUploadedFile("original.pdf", b"%PDF-1.4\noriginal")},
            )
            draft = create_draft_version(course)
            original.refresh_from_db()
            cloned = draft.sections.get()
            self.assertNotEqual(original.pdf_file.name, cloned.pdf_file.name)
            self.client.delete(f"/api/sections/{cloned.id}/pdf/")
            with original.pdf_file.open("rb") as original_file:
                self.assertTrue(original_file.read().startswith(b"%PDF-"))

    def test_admin_mutations_require_csrf_token(self):
        admin = User.objects.create_user("csrf", "csrf@example.com", "pw", is_staff=True)
        course, _ = create_course("CSRF", sections=[{"order": 1}])
        draft = create_draft_version(course)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(admin)
        denied = csrf_client.post(f"/api/course-versions/{draft.id}/publish/")
        self.assertEqual(denied.status_code, 403)
        csrf_client.get("/api/auth/status")
        token = csrf_client.cookies["csrftoken"].value
        allowed = csrf_client.post(
            f"/api/course-versions/{draft.id}/publish/",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(allowed.status_code, 200)

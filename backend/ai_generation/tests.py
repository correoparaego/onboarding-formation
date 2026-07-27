"""Tests for ai_generation (spec ai-generation, design §Testing).

These run with AI_USE_FAKE_LLM=True so NO real provider is ever contacted.
Coverage:
- PII-exclusion sanitizer strips DNI/name/email/phone and never imports employees.
- FakeLLMClient returns a parseable draft.
- generate-content returns a draft that is NOT persisted.
- BYO key set returns no key material and stores it encrypted.
- BYO configuration is validated before replacing the stored key.
- Provider HTTP error details are preserved without exposing credentials.
- multi-correct test draft is rejected at save (human-in-the-loop guard).
"""
import inspect
import io
import json
import urllib.error
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .client import FakeLLMClient, OpenAICompatibleClient, make_client
from .models import AdminLLMKey
from .sanitizer import sanitize_text
from courses.models import Course, Position

from django.contrib.auth import get_user_model

User = get_user_model()


class SanitizerTests(TestCase):
    def test_strips_dni_email_phone_and_name(self):
        dirty = (
            "Empleado: Nombre: Juan Perez, DNI 12345678Z, email juan@empresa.com, "
            "telefono +34 600 123 456. Curso de seguridad."
        )
        clean = sanitize_text(dirty)
        self.assertNotIn("12345678Z", clean)
        self.assertNotIn("juan@empresa.com", clean)
        self.assertNotIn("600 123 456", clean)
        self.assertNotIn("Juan Perez", clean)
        # Legitimate course text survives.
        self.assertIn("seguridad", clean)

    def test_sanitizer_has_no_employee_access(self):
        # HARD GUARD: the sanitizer must not import the Employee model, so it
        # is structurally impossible for it to leak a specific employee record.
        module = __import__("ai_generation.sanitizer", fromlist=["x"])
        source = inspect.getsource(module)
        # No import of the employees app (by statement) may appear.
        self.assertNotIn("import employees", source)
        self.assertNotIn("from employees", source)
        # At runtime the sanitizer module must not have bound the Employee model.
        self.assertFalse(hasattr(module, "Employee"))
        self.assertNotIn("employees", getattr(module, "__dict__", {}))


class FakeClientTests(TestCase):
    def test_content_draft_parseable(self):
        client = FakeLLMClient(mode="content")
        import json

        draft = json.loads(client.chat([{"role": "user", "content": "x"}]))
        self.assertIn("sections", draft)
        self.assertTrue(all("correct_index" not in s for s in draft["sections"]))

    def test_tests_draft_single_correct(self):
        client = FakeLLMClient(mode="tests")
        import json

        draft = json.loads(client.chat([{"role": "user", "content": "x"}]))
        for q in draft["questions"]:
            self.assertIsInstance(q["correct_index"], int)


@override_settings(AI_USE_FAKE_LLM=True)
class GenerationFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "admin", "admin@x.com", "pw", is_staff=True
        )

    def _login(self, client):
        client.force_login(self.admin)

    def test_generate_content_returns_draft_not_persisted(self):
        c = self.client
        self._login(c)
        before = Course.objects.count()
        resp = c.post(
            "/api/ai/generate-content",
            data={"course_title": "Seguridad", "answers": {"objetivo": "cumplir"}},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("draft", body)
        self.assertFalse(body["persisted"])
        self.assertEqual(Course.objects.count(), before)  # NOT persisted

    @patch("ai_generation.client.urllib.request.urlopen")
    def test_key_set_validates_model_and_returns_no_key_material(self, urlopen):
        response = urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps(
            {"data": [{"id": "gpt-4o-mini"}]}
        ).encode("utf-8")
        c = self.client
        self._login(c)
        resp = c.post(
            "/api/ai/key",
            data={
                "provider": "openai",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o-mini",
                "api_key": "sk-SUPERSECRET",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["ok"])
        self.assertNotIn("api_key", body)
        self.assertNotIn("encrypted_key", body)
        row = AdminLLMKey.objects.get(admin=self.admin)
        # Stored encrypted; raw key retrievable server-side only.
        self.assertNotEqual(row.encrypted_key, "sk-SUPERSECRET")
        self.assertEqual(row.get_raw_key(), "sk-SUPERSECRET")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.openai.com/v1/models")
        self.assertEqual(request.headers["Authorization"], "Bearer sk-SUPERSECRET")

    @patch("ai_generation.client.urllib.request.urlopen")
    def test_key_set_rejects_unavailable_model_without_replacing_key(self, urlopen):
        existing = AdminLLMKey(
            admin=self.admin,
            provider="openai",
            base_url="https://api.openai.com/v1",
            model="existing-model",
        )
        existing.set_raw_key("existing-key")
        existing.save()
        response = urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps(
            {"data": [{"id": "available-model"}]}
        ).encode("utf-8")

        c = self.client
        self._login(c)
        resp = c.post(
            "/api/ai/key",
            data={
                "provider": "Gemini API Key",
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                "model": "retired-model",
                "api_key": "new-key",
            },
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertIn("not available", resp.json()["error"])
        existing.refresh_from_db()
        self.assertEqual(existing.model, "existing-model")
        self.assertEqual(existing.get_raw_key(), "existing-key")

    @patch("ai_generation.client.urllib.request.urlopen")
    def test_provider_http_error_message_is_preserved(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError(
            url="https://example.test/v1/chat/completions",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(
                json.dumps({"error": {"message": "model is not found"}}).encode(
                    "utf-8"
                )
            ),
        )
        client = OpenAICompatibleClient(
            "https://example.test/v1", "secret", "missing-model"
        )

        with self.assertRaisesRegex(
            RuntimeError, r"LLM request failed \(404\): model is not found"
        ):
            client.chat([{"role": "user", "content": "hello"}])


@override_settings(AI_USE_FAKE_LLM=True)
class HitlSaveGuardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "admin2", "admin2@x.com", "pw", is_staff=True
        )
        self.course = Course.objects.create(title="C")

    def test_multi_correct_rejected_at_save(self):
        c = self.client
        c.force_login(self.admin)
        resp = c.post(
            "/api/banks/",
            data={
                "course_id": self.course.id,
                "questions": [
                    {
                        "text": "q",
                        "options": ["a", "b", "c"],
                        "correct_index": [0, 1],  # multi-correct -> rejected
                    }
                ],
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self.course.banks.count(), 0)

    def test_single_correct_saved(self):
        c = self.client
        c.force_login(self.admin)
        resp = c.post(
            "/api/banks/",
            data={
                "course_id": self.course.id,
                "questions": [
                    {"text": "q", "options": ["a", "b"], "correct_index": 1}
                ],
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(self.course.banks.count(), 1)

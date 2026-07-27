"""AI generation views (spec ai-generation; design §API/§Guided/§PDF flows).

All routes are admin-only (RoleIsolationMiddleware enforces /api/ai/). The raw
LLM key is never present in any response, and generated artifacts are drafts
returned for review — they are NOT persisted until the admin explicitly saves
them via the normal course/bank endpoints (human-in-the-loop, spec §HITL).
"""
import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common.parsing import json_body
from .client import OpenAICompatibleClient, make_client
from .fake_llm import fake_generate_course_content, fake_generate_test_questions
from .models import AdminLLMKey
from .prompts import build_content_prompt, build_test_prompt


def ai_key_set(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = json_body(request)
    provider = (data.get("provider") or "").strip()
    base_url = (data.get("base_url") or "").strip()
    model = (data.get("model") or "").strip()
    api_key = data.get("api_key") or ""
    if not (provider and base_url and model and api_key):
        return JsonResponse(
            {"error": "provider, base_url, model and api_key are required"},
            status=400,
        )
    try:
        OpenAICompatibleClient(base_url, api_key, model).validate_configuration()
    except RuntimeError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    row, _ = AdminLLMKey.objects.update_or_create(
        admin=request.user,
        defaults={
            "provider": provider,
            "base_url": base_url,
            "model": model,
            "status": "active",
        },
    )
    # Encrypt and store; the raw key is discarded immediately and never logged.
    row.set_raw_key(api_key)
    row.save(update_fields=["encrypted_key", "updated_at"])
    # Deliberately return NO key material (raw or ciphertext).
    return JsonResponse(
        {"ok": True, "status": row.status, "provider": row.provider, "model": row.model}
    )


def ai_key_status(request):
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)
    row = AdminLLMKey.objects.filter(admin=request.user).first()
    if row is None:
        return JsonResponse({"has_key": False, "status": None})
    return JsonResponse(
        {
            "has_key": True,
            "status": row.status,
            "provider": row.provider,
            "model": row.model,
        }
    )


def ai_generate_content(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = json_body(request)
    course_title = (data.get("course_title") or "").strip()
    answers = data.get("answers") or {}
    reference_docs = data.get("reference_docs") or []
    if not course_title:
        return JsonResponse({"error": "course_title is required"}, status=400)

    use_fake = settings.DEBUG and (
        data.get("use_fake_llm") == "true" or getattr(settings, "AI_USE_FAKE_LLM", False)
    )
    if use_fake:
        draft = fake_generate_course_content(course_title, answers, reference_docs)
        return JsonResponse({"draft": draft, "persisted": False})

    messages = build_content_prompt(course_title, answers, reference_docs)
    try:
        client = make_client("content", admin_user=request.user)
        raw = client.chat(messages)
    except RuntimeError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    try:
        draft = json.loads(raw)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "LLM did not return valid JSON", "raw": raw[:500]}, status=502
        )
    return JsonResponse({"draft": draft, "persisted": False})


def ai_generate_tests(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    use_fake = settings.DEBUG and getattr(settings, "AI_USE_FAKE_LLM", False)
    if not use_fake:
        body_data = None
        try:
            body_data = json_body(request)
        except Exception:
            pass
        if body_data and body_data.get("use_fake_llm") == "true":
            use_fake = True

    upload = request.FILES.get("file")
    pdf_text = ""
    course_title = ""

    if use_fake:
        if upload:
            pdf_text = _extract_pdf_text(upload) or ""
        else:
            body = json_body(request)
            pdf_text = (body.get("pdf_text") or "").strip()
            course_title = (body.get("course_title") or "").strip()
        if not pdf_text:
            pdf_text = "Fake PDF text"
        draft = fake_generate_test_questions(pdf_text, course_title or "Test Course")
        return JsonResponse({"draft": draft, "persisted": False})

    if upload:
        pdf_text = _extract_pdf_text(upload)
        if pdf_text is None:
            return JsonResponse(
                {"error": "could not extract text from PDF (library unavailable)"},
                status=400,
            )
    else:
        body = json_body(request)
        pdf_text = (body.get("pdf_text") or "").strip()
    if not pdf_text:
        return JsonResponse(
            {"error": "provide a PDF file or pdf_text"}, status=400
        )
    messages = build_test_prompt(pdf_text)
    try:
        client = make_client("tests", admin_user=request.user)
        raw = client.chat(messages)
    except RuntimeError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    try:
        draft = json.loads(raw)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "LLM did not return valid JSON", "raw": raw[:500]}, status=502
        )
    return JsonResponse({"draft": draft, "persisted": False})


def _extract_pdf_text(upload) -> str | None:
    """Extract text from an uploaded PDF using available libraries.

    PyPDF2 is preferred (already a dependency). Returns None if no extraction
    library is installed so the caller can fall back to ``pdf_text`` input.
    """
    try:
        import io

        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(upload.read()))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return None

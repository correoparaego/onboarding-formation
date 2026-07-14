"""AI generation views (spec ai-generation; design §API/§Guided/§PDF flows).

All routes are admin-only (RoleIsolationMiddleware enforces /api/ai/). The raw
LLM key is never present in any response, and generated artifacts are drafts
returned for review — they are NOT persisted until the admin explicitly saves
them via the normal course/bank endpoints (human-in-the-loop, spec §HITL).
"""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .client import make_client
from .models import AdminLLMKey
from .prompts import build_content_prompt, build_test_prompt


def _json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return {}


@csrf_exempt
def ai_key_set(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = _json_body(request)
    provider = (data.get("provider") or "").strip()
    base_url = (data.get("base_url") or "").strip()
    model = (data.get("model") or "").strip()
    api_key = data.get("api_key") or ""
    if not (provider and base_url and model and api_key):
        return JsonResponse(
            {"error": "provider, base_url, model and api_key are required"},
            status=400,
        )
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


@csrf_exempt
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


@csrf_exempt
def ai_generate_content(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = _json_body(request)
    course_title = (data.get("course_title") or "").strip()
    answers = data.get("answers") or {}
    reference_docs = data.get("reference_docs") or []
    if not course_title:
        return JsonResponse({"error": "course_title is required"}, status=400)
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
    # DRAFT ONLY — never persisted. The admin saves it via POST /api/courses/.
    return JsonResponse({"draft": draft, "persisted": False})


@csrf_exempt
def ai_generate_tests(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    pdf_text = ""
    upload = request.FILES.get("file")
    if upload:
        pdf_text = _extract_pdf_text(upload)
        if pdf_text is None:
            return JsonResponse(
                {"error": "could not extract text from PDF (library unavailable)"},
                status=400,
            )
    else:
        body = _json_body(request)
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
    # DRAFT ONLY — never persisted. The admin saves it via POST /api/banks/.
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

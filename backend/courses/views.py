"""Course management views (spec course-management, Phase 5).

Admin CRUD for courses (PDF upload + ordered sections), question-bank authoring
(single-correct enforced on save), and the position->catalog lookup. All routes
are admin-only (RoleIsolationMiddleware enforces /api/courses/).

Single-correct enforcement: each question stores exactly one ``correct_index``.
The save endpoint also accepts ``correct_index`` as a list and rejects it when
more than one option is marked correct (spec comprehension-test §Single Correct
and ai-generation §HITL "multiple-correct test rejected at save").
"""
import json

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common.parsing import json_body
from .models import Course, Position, Question, QuestionBank, Section


def _validate_question(q) -> int:
    """Return a single valid correct_index or raise ValidationError."""
    options = q.get("options")
    ci = q.get("correct_index")
    if not isinstance(options, list) or len(options) < 2:
        raise ValidationError("each question needs >= 2 options")
    # Multi-correct draft (correct_index given as a list) is rejected at save.
    if isinstance(ci, list):
        if len(ci) != 1:
            raise ValidationError("exactly one correct option is required")
        ci = ci[0]
    if not isinstance(ci, int) or not (0 <= ci < len(options)):
        raise ValidationError("correct_index must point to a valid option")
    return ci


def course_list_create(request):
    if request.method == "GET":
        courses = []
        for c in Course.objects.prefetch_related("position_catalog", "sections", "banks"):
            courses.append(
                {
                    "id": c.id,
                    "title": c.title,
                    "min_time_divisor": c.min_time_divisor,
                    "has_pdf": bool(c.pdf_file),
                    "positions": [p.name for p in c.position_catalog.all()],
                    "section_count": c.sections.count(),
                    "has_bank": c.banks.exists(),
                }
            )
        return JsonResponse({"courses": courses})

    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    title = (request.POST.get("title") or json_body(request).get("title") or "").strip()
    if not title:
        return JsonResponse({"error": "title is required"}, status=400)

    course = Course.objects.create(title=title)
    pdf = request.FILES.get("pdf")
    if pdf:
        course.pdf_file = pdf
        course.save(update_fields=["pdf_file"])

    # Sections passed as JSON (multipart or JSON body).
    sections_raw = request.POST.get("sections") or json_body(request).get("sections")
    if isinstance(sections_raw, str):
        try:
            sections_raw = json.loads(sections_raw)
        except json.JSONDecodeError:
            sections_raw = []
    for s in sections_raw or []:
        Section.objects.create(
            course=course,
            order=int(s.get("order", 0)),
            section_base=int(s.get("section_base", 60)),
        )

    # Position catalog mapping.
    position_ids = request.POST.getlist("position_ids") or json_body(request).get(
        "position_ids", []
    )
    if position_ids:
        course.position_catalog.set(Position.objects.filter(id__in=position_ids))

    return JsonResponse({"id": course.id, "title": course.title}, status=201)


def course_detail(request, pk):
    try:
        course = Course.objects.prefetch_related(
            "position_catalog", "sections", "banks__questions"
        ).get(pk=pk)
    except Course.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    if request.method == "DELETE":
        course.delete()
        return JsonResponse({"ok": True})

    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)

    min_time_divisor = course.min_time_divisor
    return JsonResponse(
        {
            "id": course.id,
            "title": course.title,
            "min_time_divisor": min_time_divisor,
            "positions": [p.name for p in course.position_catalog.all()],
            "sections": [
                {"order": s.order, "section_base": s.section_base}
                for s in course.sections.all()
            ],
            "banks": [
                {
                    "id": b.id,
                    "questions": [
                        {
                            "text": q.text,
                            "options": q.options,
                            "correct_index": q.correct_index,
                        }
                        for q in b.questions.all()
                    ],
                }
                for b in course.banks.all()
            ],
        }
    )


def question_bank_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = json_body(request)
    course_id = data.get("course_id")
    questions = data.get("questions") or []
    if not course_id or not questions:
        return JsonResponse(
            {"error": "course_id and questions are required"}, status=400
        )
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return JsonResponse({"error": "course not found"}, status=404)

    # Validate single-correct BEFORE writing anything (atomic reject).
    normalized = []
    try:
        for q in questions:
            ci = _validate_question(q)
            normalized.append((q.get("text", ""), q.get("options"), ci))
    except ValidationError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    with transaction.atomic():
        bank = QuestionBank.objects.create(course=course)
        for text, options, ci in normalized:
            Question.objects.create(bank=bank, text=text, options=options, correct_index=ci)
    return JsonResponse({"id": bank.id, "course_id": course.id}, status=201)


def course_catalog(request):
    """GET /api/courses/catalog?position=Operario -> mandatory courses."""
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)
    position = (request.GET.get("position") or "").strip()
    if not position:
        return JsonResponse({"error": "position query param required"}, status=400)
    from django.utils.text import slugify

    pos = (
        Position.objects.filter(name__iexact=position).first()
        or Position.objects.filter(slug__iexact=slugify(position)).first()
    )
    if pos is None:
        return JsonResponse({"position": position, "courses": []})
    courses = [
        {"id": c.id, "title": c.title} for c in pos.courses.all().order_by("title")
    ]
    return JsonResponse({"position": pos.name, "courses": courses})

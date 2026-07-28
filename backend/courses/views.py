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
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common.parsing import json_body
from .models import Course, CourseVersion, Position, Question, QuestionBank, Section
from .services import create_course, create_draft_version, publish_version


MAX_PDF_SIZE = 25 * 1024 * 1024


def _section_payload(section):
    return {
        "id": section.id,
        "order": section.order,
        "title": section.title,
        "content": section.content,
        "section_base": section.section_base,
        "has_pdf": bool(section.pdf_file),
    }


def _version_payload(version):
    return {
        "id": version.id,
        "number": version.number,
        "title": version.title,
        "min_time_divisor": version.min_time_divisor,
        "status": version.status,
        "published_at": (
            version.published_at.isoformat() if version.published_at else None
        ),
        "sections": [
            _section_payload(section) for section in version.sections.order_by("order")
        ],
    }


def _version_is_editable(version):
    return version.status == "draft" or not version.enrollments.exists()


def _validate_pdf(upload):
    if upload.size > MAX_PDF_SIZE:
        raise ValidationError("PDF exceeds the 25 MB limit")
    header = upload.read(5)
    upload.seek(0)
    if header != b"%PDF-":
        raise ValidationError("file must be a valid PDF")


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
        for c in Course.objects.filter(is_archived=False).prefetch_related(
            "position_catalog", "active_version__sections", "active_version__banks"
        ):
            version = c.active_version
            courses.append(
                {
                    "id": c.id,
                    "title": c.title,
                    "min_time_divisor": c.min_time_divisor,
                    "has_pdf": bool(
                        version and version.sections.filter(pdf_file__isnull=False).exists()
                    ),
                    "positions": [p.name for p in c.position_catalog.all()],
                    "section_count": version.sections.count() if version else 0,
                    "has_bank": version.banks.exists() if version else False,
                    "active_version": version.number if version else None,
                }
            )
        return JsonResponse({"courses": courses})

    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    body = {} if request.content_type.startswith("multipart/form-data") else json_body(request)
    title = (request.POST.get("title") or body.get("title") or "").strip()
    if not title:
        return JsonResponse({"error": "title is required"}, status=400)

    sections_raw = request.POST.get("sections") or body.get("sections")
    if isinstance(sections_raw, str):
        try:
            sections_raw = json.loads(sections_raw)
        except json.JSONDecodeError:
            sections_raw = []
    position_ids = request.POST.getlist("position_ids") or body.get(
        "position_ids", []
    )
    min_time_divisor = request.POST.get("min_time_divisor") or body.get(
        "min_time_divisor", 3
    )
    course, version = create_course(
        title,
        sections=sections_raw,
        position_ids=position_ids,
        min_time_divisor=min_time_divisor,
    )
    pdf = request.FILES.get("pdf")
    if pdf:
        course.pdf_file = pdf
        course.save(update_fields=["pdf_file"])

    return JsonResponse(
        {"id": course.id, "title": course.title, "version_id": version.id},
        status=201,
    )


def course_detail(request, pk):
    try:
        course = Course.objects.prefetch_related(
            "position_catalog", "sections", "banks__questions"
        ).get(pk=pk)
    except Course.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    if request.method == "DELETE":
        course.is_archived = True
        course.save(update_fields=["is_archived"])
        return JsonResponse({"ok": True})

    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)

    editing_version = (
        course.versions.filter(status="draft").first() or course.active_version
    )
    banks = editing_version.banks.all() if editing_version else course.banks.all()
    return JsonResponse(
        {
            "id": course.id,
            "title": course.title,
            "min_time_divisor": (
                editing_version.min_time_divisor
                if editing_version
                else course.min_time_divisor
            ),
            "positions": [
                {"id": p.id, "name": p.name} for p in course.position_catalog.all()
            ],
            "active_version": (
                _version_payload(course.active_version)
                if course.active_version
                else None
            ),
            "editing_version": (
                _version_payload(editing_version) if editing_version else None
            ),
            "versions": [
                {
                    "id": version.id,
                    "number": version.number,
                    "status": version.status,
                }
                for version in course.versions.all()
            ],
            "sections": (
                [_section_payload(section) for section in editing_version.sections.all()]
                if editing_version
                else []
            ),
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
                for b in banks
            ],
        }
    )


def course_draft(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    try:
        course = Course.objects.get(pk=pk, is_archived=False)
    except Course.DoesNotExist:
        return JsonResponse({"error": "course not found"}, status=404)
    version = create_draft_version(course)
    return JsonResponse({"version": _version_payload(version)}, status=201)


def course_version_detail(request, pk):
    try:
        version = CourseVersion.objects.select_related("course").get(pk=pk)
    except CourseVersion.DoesNotExist:
        return JsonResponse({"error": "version not found"}, status=404)
    if request.method == "GET":
        return JsonResponse({"version": _version_payload(version)})
    if request.method != "PATCH":
        return JsonResponse({"error": "method not allowed"}, status=405)
    if not _version_is_editable(version):
        return JsonResponse(
            {"error": "published versions with enrollments are immutable"},
            status=409,
        )

    data = json_body(request)
    with transaction.atomic():
        version.title = (data.get("title") or version.title).strip()
        version.min_time_divisor = max(
            1, int(data.get("min_time_divisor") or version.min_time_divisor)
        )
        version.save(update_fields=["title", "min_time_divisor"])

        sections = data.get("sections")
        if sections is not None:
            retained_ids = []
            for index, item in enumerate(sections, start=1):
                section_id = item.get("id")
                order = int(item.get("order") or index)
                section = (
                    version.sections.filter(pk=section_id).first()
                    if section_id
                    else version.sections.filter(order=order).first()
                )
                if section is None:
                    section = Section(course=version.course, version=version)
                section.order = order
                section.title = (item.get("title") or f"Sección {index}").strip()
                section.content = item.get("content") or ""
                section.section_base = max(
                    1, int(item.get("section_base") or 60)
                )
                section.save()
                retained_ids.append(section.id)
            version.sections.exclude(id__in=retained_ids).delete()

        position_ids = data.get("position_ids")
        if position_ids is not None:
            version.course.position_catalog.set(
                Position.objects.filter(id__in=position_ids)
            )
    return JsonResponse({"version": _version_payload(version)})


def course_version_publish(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    try:
        version = CourseVersion.objects.select_related("course").get(pk=pk)
    except CourseVersion.DoesNotExist:
        return JsonResponse({"error": "version not found"}, status=404)
    if not version.sections.exists():
        return JsonResponse(
            {"error": "at least one section is required"}, status=400
        )
    publish_version(version)
    return JsonResponse({"version": _version_payload(version)})


def position_list(request):
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)
    return JsonResponse(
        {
            "positions": [
                {"id": position.id, "name": position.name}
                for position in Position.objects.all()
            ]
        }
    )


def section_pdf(request, pk):
    try:
        section = Section.objects.select_related("version").get(pk=pk)
    except Section.DoesNotExist:
        return JsonResponse({"error": "section not found"}, status=404)
    if request.method == "GET":
        if not section.pdf_file:
            return JsonResponse({"error": "PDF not found"}, status=404)
        return FileResponse(
            section.pdf_file.open("rb"),
            content_type="application/pdf",
            filename=f"section-{section.id}.pdf",
        )
    if not section.version or not _version_is_editable(section.version):
        return JsonResponse({"error": "section version is immutable"}, status=409)
    if request.method == "DELETE":
        old_name = section.pdf_file.name
        storage = section.pdf_file.storage
        section.pdf_file = None
        with transaction.atomic():
            section.save(update_fields=["pdf_file"])
            if old_name:
                transaction.on_commit(lambda: storage.delete(old_name))
        return JsonResponse({"ok": True})
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    upload = request.FILES.get("pdf")
    if not upload:
        return JsonResponse({"error": "pdf is required"}, status=400)
    try:
        _validate_pdf(upload)
    except ValidationError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    storage = section.pdf_file.storage
    old_name = section.pdf_file.name
    generated_name = section.pdf_file.field.generate_filename(section, upload.name)
    try:
        new_name = storage.save(generated_name, upload)
        with transaction.atomic():
            section.pdf_file.name = new_name
            section.save(update_fields=["pdf_file"])
            if old_name and old_name != new_name:
                transaction.on_commit(lambda: storage.delete(old_name))
    except Exception:
        if "new_name" in locals():
            storage.delete(new_name)
        return JsonResponse({"error": "could not store PDF"}, status=502)
    return JsonResponse({"ok": True, "section": _section_payload(section)})


def question_bank_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = json_body(request)
    course_id = data.get("course_id")
    version_id = data.get("version_id")
    questions = data.get("questions") or []
    if not course_id or not questions:
        return JsonResponse(
            {"error": "course_id and questions are required"}, status=400
        )
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return JsonResponse({"error": "course not found"}, status=404)
    version = None
    if version_id:
        version = course.versions.filter(pk=version_id).first()
        if version is None:
            return JsonResponse({"error": "version not found"}, status=404)
    else:
        version = course.versions.filter(status="draft").first() or course.active_version

    # Validate single-correct BEFORE writing anything (atomic reject).
    normalized = []
    try:
        for q in questions:
            ci = _validate_question(q)
            normalized.append((q.get("text", ""), q.get("options"), ci))
    except ValidationError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    with transaction.atomic():
        bank = QuestionBank.objects.create(course=course, version=version)
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

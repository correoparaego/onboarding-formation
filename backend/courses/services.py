from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from .models import Course, CourseVersion, Question, QuestionBank, Section


@transaction.atomic
def ensure_active_version(course):
    if course.active_version_id:
        return course.active_version
    course = Course.objects.select_for_update().get(pk=course.pk)
    if course.active_version_id:
        return course.active_version
    next_number = (course.versions.aggregate(value=Max("number"))["value"] or 0) + 1
    version = CourseVersion.objects.create(
        course=course,
        number=next_number,
        title=course.title,
        min_time_divisor=course.min_time_divisor,
        status="published",
        published_at=timezone.now(),
    )
    course.sections.filter(version__isnull=True).update(version=version)
    course.banks.filter(version__isnull=True).update(version=version)
    course.active_version = version
    course.save(update_fields=["active_version"])
    return version


@transaction.atomic
def create_course(title, sections=None, position_ids=None, min_time_divisor=3):
    course = Course.objects.create(
        title=title,
        min_time_divisor=max(1, int(min_time_divisor or 3)),
    )
    version = CourseVersion.objects.create(
        course=course,
        number=1,
        title=title,
        min_time_divisor=course.min_time_divisor,
        status="published",
        published_at=timezone.now(),
    )
    for index, section in enumerate(sections or [], start=1):
        Section.objects.create(
            course=course,
            version=version,
            order=int(section.get("order") or index),
            title=(section.get("title") or f"Sección {index}").strip(),
            content=section.get("content") or "",
            section_base=max(1, int(section.get("section_base") or 60)),
        )
    course.active_version = version
    course.save(update_fields=["active_version"])
    if position_ids:
        course.position_catalog.set(position_ids)
    return course, version


@transaction.atomic
def create_draft_version(course):
    existing = course.versions.filter(status="draft").first()
    if existing:
        return existing

    source = course.active_version
    next_number = (course.versions.aggregate(value=Max("number"))["value"] or 0) + 1
    version = CourseVersion.objects.create(
        course=course,
        number=next_number,
        title=source.title if source else course.title,
        min_time_divisor=(
            source.min_time_divisor if source else course.min_time_divisor
        ),
    )
    source_sections = source.sections.all() if source else course.sections.all()
    for section in source_sections:
        Section.objects.create(
            course=course,
            version=version,
            order=section.order,
            title=section.title,
            content=section.content,
            pdf_file=section.pdf_file.name if section.pdf_file else None,
            section_base=section.section_base,
        )
    if source:
        for bank in source.banks.prefetch_related("questions"):
            new_bank = QuestionBank.objects.create(course=course, version=version)
            Question.objects.bulk_create(
                [
                    Question(
                        bank=new_bank,
                        text=question.text,
                        options=question.options,
                        correct_index=question.correct_index,
                    )
                    for question in bank.questions.all()
                ]
            )
    return version


@transaction.atomic
def publish_version(version):
    if version.status != "draft":
        return version
    course = version.course
    if course.active_version_id:
        CourseVersion.objects.filter(pk=course.active_version_id).update(
            status="archived"
        )
    version.status = "published"
    version.published_at = timezone.now()
    version.save(update_fields=["status", "published_at"])
    course.active_version = version
    course.title = version.title
    course.min_time_divisor = version.min_time_divisor
    course.save(update_fields=["active_version", "title", "min_time_divisor"])
    return version

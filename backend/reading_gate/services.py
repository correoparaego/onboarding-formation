"""Reading-gate and comprehension-test services (spec timed-reading,
comprehension-test; design §Reading-Gate Sequence / §Comprehension-Test Flow).

Server-authoritative compliance core. The client heartbeats are UNTRUSTED input:
every gate decision (section unlock, test unlock, attempt cap) is computed here
on the server from persisted `ReadingProgress`, never from client claims.

Two independent concerns live in this module:

1. Enrollment assignment (Phase 7) — `assign_mandatory_courses`.
2. Timed reading gate + comprehension test (Phase 9/10) — `process_heartbeat`,
   `get_test_subset`, `get_test_questions`, `grade_submission`.
"""
import hashlib
import logging
import math
import random

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from courses.models import Course, Position, Question
from reading_gate.models import AuditEvent, Enrollment, ReadingProgress

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tunable policy (kept explicit so the product owner can adjust without diving
# into the logic). Documented deviations from the open spec are noted in
# apply-progress.md.
# ---------------------------------------------------------------------------

# Maximum seconds of active time a single heartbeat may credit. Heartbeats are
# sent periodically by the client; an absurd delta is clamped (never trusted)
# to limit time-inflation fraud while still accepting legitimate long pauses
# between heartbeats.
MAX_HEARTBEAT_DELTA = 120

# Number of questions drawn per attempt. The deterministic shuffle guarantees a
# DISTINCT subset across attempts whenever the bank holds more than this many
# questions; if the bank is smaller, the whole bank is used (still deterministically
# ordered per attempt).
TEST_SUBSET_SIZE = 5

# Passing grade: fraction of the attempt's subset that must be correct.
# 1.0 == every question must be answered correctly (strict compliance default).
TEST_PASS_THRESHOLD = 1.0


# ---------------------------------------------------------------------------
# Enrollment assignment
# ---------------------------------------------------------------------------
@transaction.atomic
def assign_courses(employee, courses, source="manual", assigned_by=None, notify=True):
    from courses.services import ensure_active_version

    created = []
    for course in courses:
        if course.is_archived:
            continue
        version = ensure_active_version(course)
        if Enrollment.objects.filter(employee=employee, course=course).exists():
            continue
        enrollment = Enrollment.objects.create(
            employee=employee,
            course=course,
            course_version=version,
            cycle=1,
            source=source,
            assigned_by=assigned_by,
        )
        created.append(enrollment)
        _audit(
            enrollment,
            "enrollment_assigned",
            "",
            "",
            {
                "course_id": course.id,
                "course_version_id": version.id,
                "source": source,
            },
        )
    if created and notify:
        enrollment_id = created[0].id

        def deliver_access():
            try:
                from notifications import services as notify_services

                enrollment = Enrollment.objects.select_related("employee").get(
                    pk=enrollment_id
                )
                notify_services.issue_access_token(enrollment)
            except Exception as exc:
                logger.warning("access token issuance failed: %s", exc)

        transaction.on_commit(deliver_access)
    return created


def assign_mandatory_courses(employee) -> int:
    from django.utils.text import slugify

    position = employee.current_position
    if position is None:
        position = (
            Position.objects.filter(name__iexact=employee.position).first()
            or Position.objects.filter(
                slug__iexact=slugify(employee.position)
            ).first()
        )
    if position is None:
        return 0
    courses = position.courses.filter(is_archived=False)
    return len(assign_courses(employee, courses, source="position"))


def resolve_assignment_employees(
    employee_ids=None, position_ids=None, include_ids=None, exclude_ids=None
):
    from employees.models import Employee

    selected_ids = set(employee_ids or []) | set(include_ids or [])
    if position_ids:
        selected_ids.update(
            Employee.objects.filter(current_position_id__in=position_ids).values_list(
                "id", flat=True
            )
        )
    selected_ids.difference_update(exclude_ids or [])
    return Employee.objects.filter(id__in=selected_ids).order_by("name")


@transaction.atomic
def apply_assignment(
    course_ids,
    employee_ids=None,
    position_ids=None,
    include_ids=None,
    exclude_ids=None,
    assigned_by=None,
):
    employees = resolve_assignment_employees(
        employee_ids, position_ids, include_ids, exclude_ids
    )
    courses = list(
        Course.objects.filter(
            id__in=course_ids, is_archived=False
        )
    )
    created = []
    for employee in employees:
        created.extend(
            assign_courses(
                employee,
                courses,
                source="manual",
                assigned_by=assigned_by,
                notify=True,
            )
        )
    return created


@transaction.atomic
def change_enrollment_status(enrollment, action, actor=None):
    transitions = {
        "pause": ({"assigned", "in_progress"}, "paused"),
        "resume": ({"paused"}, "in_progress"),
        "cancel": ({"assigned", "in_progress", "paused", "complete"}, "cancelled"),
    }
    if action not in transitions:
        raise ValueError("unsupported enrollment action")
    allowed, target = transitions[action]
    if enrollment.status not in allowed:
        raise ValueError(f"cannot {action} enrollment in {enrollment.status}")
    enrollment.status = target
    enrollment.paused_at = timezone.now() if target == "paused" else None
    if target == "cancelled":
        enrollment.cancelled_at = timezone.now()
    enrollment.save(update_fields=["status", "paused_at", "cancelled_at"])
    _audit(enrollment, f"enrollment_{target}", "", "", {"actor_id": getattr(actor, "id", None)})
    return enrollment


@transaction.atomic
def repeat_enrollment(enrollment, actor=None):
    if enrollment.status not in {"cancelled", "passed", "failed_exhausted"}:
        raise ValueError("only terminal enrollments can be repeated")
    next_cycle = (
        Enrollment.objects.filter(
            employee=enrollment.employee, course=enrollment.course
        ).aggregate(value=Max("cycle"))["value"]
        or 0
    ) + 1
    repeated = Enrollment.objects.create(
        employee=enrollment.employee,
        course=enrollment.course,
        course_version=enrollment.course.active_version or enrollment.course_version,
        cycle=next_cycle,
        source="repeat",
        assigned_by=actor,
    )
    _audit(
        repeated,
        "enrollment_repeated",
        "",
        "",
        {"previous_enrollment_id": enrollment.id, "cycle": next_cycle},
    )
    return repeated


# ---------------------------------------------------------------------------
# Reading gate
# ---------------------------------------------------------------------------
def min_time_for_section(section, divisor) -> int:
    """Server-authoritative minimum active reading time for a section.

    minTimePerSection = section_base / course.min_time_divisor, rounded UP so a
    partial second still requires the full threshold. Guards against a zero
    base (returns 1s) so a section can never be unlocked instantly.
    """
    divisor = max(1, int(divisor))
    return max(1, math.ceil(section.section_base / divisor))


def enrollment_sections(enrollment):
    if enrollment.course_version_id:
        return enrollment.course_version.sections.order_by("order")
    return enrollment.course.sections.order_by("order")


def enrollment_time_divisor(enrollment):
    if enrollment.course_version_id:
        return enrollment.course_version.min_time_divisor
    return enrollment.course.min_time_divisor


def section_is_unlocked(enrollment, section):
    if enrollment.status in ("paused", "cancelled"):
        return False
    sections = list(enrollment_sections(enrollment))
    try:
        index = next(i for i, item in enumerate(sections) if item.id == section.id)
    except StopIteration:
        return False
    if index == 0:
        return True
    previous = sections[index - 1]
    progress = ReadingProgress.objects.filter(
        enrollment=enrollment, section=previous
    ).first()
    accumulated = progress.accumulated_time if progress else 0
    return accumulated >= min_time_for_section(
        previous, enrollment_time_divisor(enrollment)
    )


def _all_sections_complete(enrollment, divisor) -> bool:
    sections = list(enrollment_sections(enrollment))
    if not sections:
        return False
    for section in sections:
        min_time = min_time_for_section(section, divisor)
        progress = ReadingProgress.objects.filter(
            enrollment=enrollment, section=section
        ).first()
        if progress is None or progress.accumulated_time < min_time:
            return False
    return True


def process_heartbeat(enrollment, section_order, delta, visibility, interaction,
                      device_id="", session_id="", request=None):
    """Validate + accumulate one reading heartbeat. Returns a status dict.

    Server-authoritative rules:
    - The requested section is only reachable if the PREVIOUS section has met
      its min-time threshold (sequential unlock). Section 1 is always allowed.
    - Time is credited ONLY when the client reports BOTH visibility and
      interaction as true (the API "validates" the signals; this is the
      RGPD-accepted "reasonable control" — it cannot prove human presence).
    - The credited delta is clamped to MAX_HEARTBEAT_DELTA.
    - Cross-device resume is implicit: ReadingProgress is keyed by
      (enrollment, section), so a new device simply continues accumulating.
    """
    if enrollment.status in ("paused", "cancelled"):
        return {
            "error": f"enrollment is {enrollment.status}",
            "status_code": 409,
        }
    divisor = enrollment_time_divisor(enrollment)
    sections = list(enrollment_sections(enrollment))
    section = next((s for s in sections if s.order == section_order), None)
    if section is None:
        return {"error": "section not found", "status_code": 404}

    # Sequential unlock gate: previous section must be complete.
    locked = not section_is_unlocked(enrollment, section)

    min_time = min_time_for_section(section, divisor)

    if locked:
        # Do NOT credit while the gate is locked.
        return {
            "locked": True,
            "section_order": section_order,
            "min_time": min_time,
            "enrollment_status": enrollment.status,
            "test_unlocked": enrollment.status in ("complete", "passed"),
            "status_code": 200,
        }

    # Validate + clamp the delta (untrusted input).
    try:
        delta = int(delta)
    except (TypeError, ValueError):
        delta = 0
    if delta < 0:
        delta = 0
    credited = min(delta, MAX_HEARTBEAT_DELTA) if (visibility and interaction) else 0

    progress, _ = ReadingProgress.objects.get_or_create(
        enrollment=enrollment, section=section,
        defaults={"device_id": device_id, "session_id": session_id},
    )
    was_complete = progress.accumulated_time >= min_time
    progress.accumulated_time += credited
    progress.reached_section = section.order
    if device_id:
        progress.device_id = device_id
    if session_id:
        progress.session_id = session_id
    progress.save(update_fields=["accumulated_time", "reached_section", "device_id", "session_id"])

    if credited and enrollment.status == "assigned":
        enrollment.status = "in_progress"
        enrollment.save(update_fields=["status"])

    now_complete = progress.accumulated_time >= min_time
    if now_complete and not was_complete:
        _audit(enrollment, "section_complete", device_id, session_id,
               {"section_order": section.order, "accumulated": progress.accumulated_time,
                "min_time": min_time})
        # Record the sequential unlock so the audit trail captures
        # "section unlock/complete" (spec audit-log §Coverage).
        next_section = next(
            (s for s in sections if s.order == section.order + 1), None
        )
        if next_section is not None:
            _audit(enrollment, "section_unlock", device_id, session_id,
                   {"from_section_order": section.order,
                    "unlocked_section_order": next_section.order})

    # All-sections-complete → unlock the comprehension test.
    all_complete = _all_sections_complete(enrollment, divisor)
    if all_complete and enrollment.status not in ("complete", "passed"):
        enrollment.status = "complete"
        enrollment.save(update_fields=["status"])
        _audit(enrollment, "reading_complete", device_id, session_id,
               {"sections": len(sections), "enrollment_status": "complete"})

    return {
        "locked": False,
        "enrollment_id": enrollment.id,
        "section_order": section.order,
        "accumulated": progress.accumulated_time,
        "min_time": min_time,
        "remaining": max(0, min_time - progress.accumulated_time),
        "credited": credited,
        "section_complete": now_complete,
        "unlocked_next": now_complete,
        "all_sections_complete": all_complete,
        "enrollment_status": enrollment.status,
        "test_unlocked": enrollment.status in ("complete", "passed"),
        "status_code": 200,
    }


# ---------------------------------------------------------------------------
# Comprehension test
# ---------------------------------------------------------------------------
def _subset_seed(enrollment_id, attempt_no) -> int:
    """Deterministic, process-stable seed for an attempt's question subset.

    Uses SHA-256 (NOT Python's salted `hash()`) so the same enrollment+attempt
    always yields the same subset across processes and restarts.
    """
    digest = hashlib.sha256(f"{enrollment_id}:{attempt_no}".encode()).hexdigest()
    return int(digest[:16], 16)


def get_test_subset(enrollment, attempt_no):
    """Return the ordered list of Question objects for an attempt.

    Deterministic DISTINCT subset: all questions across the course's banks are
    shuffled by a seed derived from (enrollment_id, attempt_no), then the first
    TEST_SUBSET_SIZE are taken. Different attempts → different seeds → different
    subsets (when the bank is larger than the subset size).
    """
    questions = Question.objects.filter(bank__course=enrollment.course)
    if enrollment.course_version_id:
        questions = questions.filter(bank__version=enrollment.course_version)
    questions = list(questions)
    if not questions:
        return []
    rng = random.Random(_subset_seed(enrollment.id, attempt_no))
    rng.shuffle(questions)
    return questions[: min(len(questions), TEST_SUBSET_SIZE)]


def get_test_questions(enrollment, device_id="", session_id=""):
    """Build the question payload for the CURRENT attempt (attempts_used + 1).

    Does NOT consume an attempt — that only happens on submit. Emits an
    `attempt_start` audit event so the audit trail records the attempt view.
    Returns a dict with `status_code` for the caller to translate to HTTP.
    """
    if enrollment.status != "complete":
        return {
            "error": "reading must be completed before the test",
            "test_unlocked": False,
            "status_code": 409,
        }
    if enrollment.attempts_used >= 3:
        return {
            "error": "maximum attempts exhausted",
            "enrollment_status": enrollment.status,
            "status_code": 409,
        }
    attempt_no = enrollment.attempts_used + 1
    subset = get_test_subset(enrollment, attempt_no)
    if not subset:
        return {"error": "course has no questions", "status_code": 400}

    _audit(enrollment, "attempt_start", device_id, session_id,
           {"attempt_no": attempt_no, "subset_size": len(subset)})

    return {
        "enrollment_id": enrollment.id,
        "attempt_no": attempt_no,
        "attempts_remaining": 3 - enrollment.attempts_used,
        "test_unlocked": enrollment.status in ("complete", "passed"),
        # correct_index is intentionally withheld from the client.
        "questions": [
            {"id": q.id, "text": q.text, "options": q.options} for q in subset
        ],
        "status_code": 200,
    }


def grade_submission(enrollment, answers, device_id="", session_id=""):
    """Grade one comprehension-test attempt and update enrollment state.

    Server-authoritative attempt cap: a 4th submission (attempts_used already
    3) is BLOCKED and the enrollment is marked `failed_exhausted`.

    On FAIL: ReadingProgress is reset to section 1 / 0s and attempts_used is
    incremented; the employee must re-read before retrying. On PASS: enrollment
    status becomes `passed` (certificate + badge evaluation are later phases).
    """
    # Blocked 4th attempt (or already passed).
    if enrollment.status == "passed":
        return {"error": "enrollment already passed", "enrollment_status": "passed",
                "status_code": 409}
    if enrollment.attempts_used >= 3:
        if enrollment.status != "failed_exhausted":
            enrollment.status = "failed_exhausted"
            enrollment.save(update_fields=["status"])
        _write_expediente(enrollment, None, None, passed=False)
        _audit(enrollment, "attempt_blocked", device_id, session_id,
               {"reason": "4th attempt blocked", "attempts_used": enrollment.attempts_used})
        return {
            "error": "maximum attempts exceeded",
            "enrollment_status": enrollment.status,
            "status_code": 409,
        }
    if enrollment.status != "complete":
        return {
            "error": "reading must be completed before the test",
            "enrollment_status": enrollment.status,
            "status_code": 409,
        }

    attempt_no = enrollment.attempts_used + 1
    subset = get_test_subset(enrollment, attempt_no)
    if not subset:
        return {"error": "course has no questions", "status_code": 400}

    correct_by_id = {q.id: q.correct_index for q in subset}
    answered = {a.get("question_id"): a.get("selected_index") for a in (answers or [])}
    score = sum(
        1 for q in subset
        if answered.get(q.id) == correct_by_id[q.id]
    )
    total = len(subset)
    passed = (total > 0) and ((score / total) >= TEST_PASS_THRESHOLD)

    enrollment.attempts_used += 1

    if passed:
        enrollment.status = "passed"
        enrollment.save(update_fields=["status", "attempts_used"])
        _on_pass(enrollment, score, total)
        _audit(enrollment, "attempt_submit", device_id, session_id,
               {"attempt_no": attempt_no, "score": score, "total": total, "passed": True})
        return {
            "result": "pass",
            "score": score,
            "total": total,
            "attempts_used": enrollment.attempts_used,
            "attempts_remaining": max(0, 3 - enrollment.attempts_used),
            "enrollment_status": "passed",
            "certificate_available": True,
            "status_code": 200,
        }

    # FAIL: reset reading so the employee must re-read before the next attempt.
    ReadingProgress.objects.filter(enrollment=enrollment).delete()
    enrollment.status = "in_progress"
    enrollment.save(update_fields=["status", "attempts_used"])
    _audit(enrollment, "attempt_submit", device_id, session_id,
           {"attempt_no": attempt_no, "score": score, "total": total, "passed": False})
    _audit(enrollment, "attempt_fail", device_id, session_id,
           {"attempts_used": enrollment.attempts_used, "reading_reset": True})
    return {
        "result": "fail",
        "score": score,
        "total": total,
        "attempts_used": enrollment.attempts_used,
        "attempts_remaining": max(0, 3 - enrollment.attempts_used),
        "enrollment_status": "in_progress",
        "reading_reset": True,
        "status_code": 200,
    }


# ---------------------------------------------------------------------------
# Audit helper — append-only, NO DNI / raw token / PII in payloads.
# ---------------------------------------------------------------------------
def audit_event(enrollment, event_type, device_id, session_id, payload):
    """Public append-only audit helper (spec audit-log §Append-Only).

    Emits an immutable ``AuditEvent``. Callers MUST NOT place DNI, raw tokens,
    or any PII in ``payload`` — reference the enrollment id + metadata only.
    The API layer never exposes create/update/delete, and the Django admin
    registers ``AuditEvent`` as read-only, so immutability holds end-to-end.
    """
    AuditEvent.objects.create(
        enrollment=enrollment,
        event_type=event_type,
        device_id=device_id or "",
        session_id=session_id or "",
        payload=payload,
    )


# Internal alias — kept so in-module callers (process_heartbeat, grade_submission,
# assign_mandatory_courses) keep working without churn.
def _audit(enrollment, event_type, device_id, session_id, payload):
    return audit_event(enrollment, event_type, device_id, session_id, payload)


# ---------------------------------------------------------------------------
# Post-result side effects (PR5): expediente persistence + badges + completion.
# ---------------------------------------------------------------------------
def _write_expediente(enrollment, score, total, passed):
    """Persist/update the per-enrollment result (spec expediente §Result Storage)."""
    from reading_gate.models import Expediente

    exp, _ = Expediente.objects.get_or_create(
        enrollment=enrollment,
        defaults={
            "employee": enrollment.employee,
            "course": enrollment.course,
            "status": enrollment.status,
            "attempts_used": enrollment.attempts_used,
        },
    )
    exp.employee = enrollment.employee
    exp.course = enrollment.course
    exp.status = enrollment.status
    exp.attempts_used = enrollment.attempts_used
    if passed:
        exp.score = score
        exp.total = total
        exp.completed_at = timezone.now()
    exp.save()


def _on_pass(enrollment, score, total):
    """Record expediente + award badges + notify completion on a passing result."""
    _write_expediente(enrollment, score, total, passed=True)
    try:
        from certificates import services as cert_services

        cert_services.award_badges_on_pass(enrollment)
    except Exception as exc:  # badges must never break the pass result
        logger.warning("badge award failed: %s", exc)
    try:
        from notifications import services as notify

        notify.send_completion(enrollment)
    except Exception as exc:  # completion email is best-effort
        logger.warning("completion email failed: %s", exc)

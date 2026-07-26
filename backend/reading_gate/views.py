"""HTTP endpoints for the timed reading gate and comprehension test.

Both route groups are employee-only (RoleIsolationMiddleware enforces
`/api/reading/` and `/api/test/` as EMPLOYEE_PREFIXES). The employee identity
is taken from the session established by `employee_redeem` — never from the
request body, so one employee cannot act on another's enrollment.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common.parsing import json_body
from reading_gate import services
from reading_gate.models import AuditEvent, Enrollment, Expediente


def _employee_id(request):
    return request.session.get("employee_id")


def _owned_enrollment(enrollment_id, employee_id):
    """Return (enrollment, error_dict). Error_dict is None on success."""
    try:
        enrollment = Enrollment.objects.select_related("course").get(pk=enrollment_id)
    except Enrollment.DoesNotExist:
        return None, {"error": "enrollment not found", "status_code": 404}
    if enrollment.employee_id != employee_id:
        # Do not reveal existence to other employees.
        return None, {"error": "enrollment not found", "status_code": 404}
    return enrollment, None


@csrf_exempt
def reading_heartbeat(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    employee_id = _employee_id(request)
    if not employee_id:
        return JsonResponse({"error": "employee authentication required"}, status=403)

    body = json_body(request)
    enrollment, err = _owned_enrollment(body.get("enrollment_id"), employee_id)
    if err:
        return JsonResponse({"error": err["error"]}, status=err["status_code"])

    result = services.process_heartbeat(
        enrollment=enrollment,
        section_order=int(body.get("section_order", 1)),
        delta=body.get("delta", 0),
        visibility=bool(body.get("visibility", False)),
        interaction=bool(body.get("interaction", False)),
        device_id=body.get("device_id", "") or "",
        session_id=body.get("session_id", "") or "",
    )
    return JsonResponse(
        {k: v for k, v in result.items() if k != "status_code"},
        status=result.get("status_code", 200),
    )


@csrf_exempt
def test_questions(request):
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)
    employee_id = _employee_id(request)
    if not employee_id:
        return JsonResponse({"error": "employee authentication required"}, status=403)

    enrollment_id = request.GET.get("enrollment_id")
    enrollment, err = _owned_enrollment(enrollment_id, employee_id)
    if err:
        return JsonResponse({"error": err["error"]}, status=err["status_code"])

    result = services.get_test_questions(enrollment)
    return JsonResponse(
        {k: v for k, v in result.items() if k != "status_code"},
        status=result.get("status_code", 200),
    )


@csrf_exempt
def test_submit(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    employee_id = _employee_id(request)
    if not employee_id:
        return JsonResponse({"error": "employee authentication required"}, status=403)

    body = json_body(request)
    enrollment, err = _owned_enrollment(body.get("enrollment_id"), employee_id)
    if err:
        return JsonResponse({"error": err["error"]}, status=err["status_code"])

    result = services.grade_submission(
        enrollment=enrollment,
        answers=body.get("answers", []),
        device_id=body.get("device_id", "") or "",
        session_id=body.get("session_id", "") or "",
    )
    return JsonResponse(
        {k: v for k, v in result.items() if k != "status_code"},
        status=result.get("status_code", 200),
    )


def expediente_list(request):
    """Admin filter of expediente records (spec expediente §Admin Filter).

    Query params: ``course`` (Course id or title) and ``status`` (enrollment
    status). Admin-only via RoleIsolationMiddleware.
    """
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)
    qs = Expediente.objects.select_related("employee", "course", "enrollment").all()

    course = request.GET.get("course")
    if course:
        if course.isdigit():
            qs = qs.filter(course_id=int(course))
        else:
            qs = qs.filter(course__title__iexact=course)

    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    total = qs.count()
    limit = min(int(request.GET.get("limit", 50)), 200)
    offset = int(request.GET.get("offset", 0))
    page = qs[offset : offset + limit]

    rows = [
        {
            "employee_id": e.employee_id,
            "employee_name": e.employee.name,
            "dni": e.employee.dni,
            "course_id": e.course_id,
            "course_title": e.course.title,
            "status": e.status,
            "attempts_used": e.attempts_used,
            "score": e.score,
            "total": e.total,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in page
    ]
    return JsonResponse({"count": total, "limit": limit, "offset": offset, "results": rows})


def audit_list(request):
    """Admin-only, read-only audit log (spec audit-log §Append-Only / §No Mutation).

    GET /api/audit?enrollment=<id>&employee=<id>&event_type=<str>&date=<YYYY-MM-DD>

    The audit log is the compliance artifact: it is append-only. NO create,
    update, or delete endpoint is exposed — any non-GET method is rejected with
    405 so mutation is impossible through the API. Records are also read-only in
    the Django admin (see reading_gate/admin.py).
    """
    if request.method != "GET":
        return JsonResponse(
            {"error": "audit log is append-only; create/update/delete not allowed"},
            status=405,
        )
    qs = AuditEvent.objects.select_related("enrollment").all()

    enrollment = request.GET.get("enrollment")
    if enrollment and enrollment.isdigit():
        qs = qs.filter(enrollment_id=int(enrollment))
    employee = request.GET.get("employee")
    if employee and employee.isdigit():
        qs = qs.filter(enrollment__employee_id=int(employee))
    event_type = request.GET.get("event_type")
    if event_type:
        qs = qs.filter(event_type=event_type)
    date = request.GET.get("date")
    if date:
        qs = qs.filter(timestamp__date=date)

    total = qs.count()
    limit = min(int(request.GET.get("limit", 100)), 500)
    offset = int(request.GET.get("offset", 0))
    page = qs[offset : offset + limit]

    rows = [
        {
            "id": e.id,
            "event_type": e.event_type,
            "enrollment_id": e.enrollment_id,
            "device_id": e.device_id,
            "session_id": e.session_id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "payload": e.payload,
        }
        for e in page
    ]
    return JsonResponse({"count": total, "limit": limit, "offset": offset, "results": rows})


def employee_enrollments(request):
    """Employee-only endpoint to list their enrollments."""
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)
    employee_id = _employee_id(request)
    if not employee_id:
        return JsonResponse({"error": "employee authentication required"}, status=403)

    enrollments = Enrollment.objects.filter(employee_id=employee_id).select_related("course")
    rows = [
        {
            "id": e.id,
            "course_id": e.course_id,
            "course_title": e.course.title,
            "status": e.status,
            "attempts_used": e.attempts_used,
            "score": e.score,
            "total": e.total,
        }
        for e in enrollments
    ]
    return JsonResponse({"enrollments": rows})

"""HTTP endpoints for the timed reading gate and comprehension test.

Both route groups are employee-only (RoleIsolationMiddleware enforces
`/api/reading/` and `/api/test/` as EMPLOYEE_PREFIXES). The employee identity
is taken from the session established by `employee_redeem` — never from the
request body, so one employee cannot act on another's enrollment.
"""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from reading_gate import services
from reading_gate.models import Enrollment


def _json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return {}


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

    body = _json_body(request)
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

    body = _json_body(request)
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

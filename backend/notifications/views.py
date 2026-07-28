"""Admin endpoints for secure-access issuance (admin-only)."""
import logging

from django.http import JsonResponse

from common.parsing import json_body
from common.rate_limit import access_code_rate_limit
from employees.models import Employee
from notifications import services as notify
from reading_gate import services as reading_services
from reading_gate.models import Enrollment


MAX_BATCH_SIZE = 100
logger = logging.getLogger(__name__)


def admin_resend_access(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    try:
        enrollment = Enrollment.objects.select_related("employee", "course").get(pk=pk)
    except Enrollment.DoesNotExist:
        return JsonResponse({"error": "enrollment not found"}, status=404)
    notify.resend_access_token(enrollment)
    # Raw token/code are intentionally NOT echoed back in the response.
    return JsonResponse(
        {"ok": True, "enrollment_id": enrollment.id, "employee": enrollment.employee.name}
    )


@access_code_rate_limit
def admin_batch_access(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({"error": "JSON body must be an object"}, status=400)
    raw_ids = data.get("employee_ids") or []
    if not isinstance(raw_ids, list):
        return JsonResponse({"error": "employee_ids must be a list"}, status=400)
    try:
        employee_ids = list(dict.fromkeys(int(value) for value in raw_ids))
    except (TypeError, ValueError):
        return JsonResponse({"error": "employee_ids must contain integers"}, status=400)
    if not employee_ids:
        return JsonResponse({"error": "employee_ids are required"}, status=400)
    if len(employee_ids) > MAX_BATCH_SIZE:
        return JsonResponse(
            {"error": f"maximum batch size is {MAX_BATCH_SIZE}"}, status=400
        )

    employees = {
        employee.id: employee
        for employee in Employee.objects.filter(id__in=employee_ids).prefetch_related(
            "enrollments"
        )
    }
    results = []
    errors = []
    for employee_id in employee_ids:
        employee = employees.get(employee_id)
        if employee is None:
            continue
        enrollment = employee.enrollments.exclude(status="cancelled").first()
        try:
            token_row, raw_token, code = notify.rotate_employee_access(
                employee, enrollment=enrollment
            )
        except Exception as exc:
            logger.warning("employee access rotation failed for %s: %s", employee.id, exc)
            errors.append({"employee_id": employee.id, "error": "generation_failed"})
            continue
        try:
            delivery = notify.deliver_access_code(
                employee, raw_token, code, allow_console=False
            )
        except Exception as exc:
            logger.warning("employee access delivery failed for %s: %s", employee.id, exc)
            from notifications.transports import EmailResult

            delivery = EmailResult(False, "delivery_failed")
        delivery_status = "sent" if delivery.ok else (
            "skipped" if not employee.email else "failed"
        )
        try:
            reading_services.audit_event(
                enrollment,
                "employee_access_rotated",
                "",
                "",
                {
                    "employee_id": employee.id,
                    "actor_id": request.user.id,
                    "delivery_status": delivery_status,
                    "batch": True,
                },
            )
        except Exception as exc:
            logger.warning("employee access audit failed for %s: %s", employee.id, exc)
        results.append(
            {
                "employee_id": employee.id,
                "employee_name": employee.name,
                "email": employee.email,
                "code": code,
                "delivery_status": delivery_status,
                "expires_at": token_row.expires_at.isoformat(),
            }
        )

    response = JsonResponse(
        {
            "results": results,
            "missing_employee_ids": [
                employee_id for employee_id in employee_ids if employee_id not in employees
            ],
            "errors": errors,
        },
        status=201,
    )
    response["Cache-Control"] = "no-store, private"
    response["Pragma"] = "no-cache"
    return response

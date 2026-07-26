"""Admin endpoints for secure-access resend (admin-only via RoleIsolationMiddleware)."""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from notifications import services as notify
from reading_gate.models import Enrollment


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

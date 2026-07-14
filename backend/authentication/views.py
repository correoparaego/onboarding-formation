"""Authentication views (spec authentication).

- ``POST /api/auth/admin/login``  — username/password -> Django session (staff).
- ``POST /api/auth/admin/logout`` — invalidates the admin session.
- ``POST /api/auth/employee/redeem`` — redeem a magic-link token or code;
  on success establishes an employee-scoped session (no Django user).

CSRF is exempted here so the SPA can call these without a token dance; a
proper CSRF token flow belongs with the SPA security wiring (later phase).
This is a deliberate, documented MVP trade-off.
"""
import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import EmployeeAccessToken


def _json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return {}


@csrf_exempt
def admin_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = _json_body(request)
    username = data.get("username", "")
    password = data.get("password", "")
    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_staff:
        return JsonResponse({"error": "invalid credentials"}, status=401)
    login(request, user)
    # A staff login must never carry an employee session.
    request.session.pop("employee_id", None)
    return JsonResponse({"ok": True, "user": {"username": user.username}})


@csrf_exempt
def admin_logout(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    logout(request)
    return JsonResponse({"ok": True})


@csrf_exempt
def employee_redeem(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = _json_body(request)
    value = data.get("token") or data.get("code") or ""
    employee, status = EmployeeAccessToken.redeem(value)
    if employee is None:
        return JsonResponse({"error": f"token {status}"}, status=401)
    # Establish an employee-scoped session. We do NOT authenticate a Django
    # user — the employee identity lives only in the session under employee_id.
    request.session["employee_id"] = employee.id
    request.session["employee_name"] = employee.name
    return JsonResponse(
        {"ok": True, "employee": {"id": employee.id, "name": employee.name}}
    )

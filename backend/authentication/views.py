"""Authentication views (spec authentication).

- ``POST /api/auth/admin/login``  — username/password -> Django session (staff).
- ``POST /api/auth/admin/logout`` — invalidates the admin session.
- ``POST /api/auth/employee/redeem`` — redeem a magic-link token or code;
  on success establishes an employee-scoped session (no Django user).

CSRF is exempted here so the SPA can call these without a token dance; a
proper CSRF token flow belongs with the SPA security wiring (later phase).
This is a deliberate, documented MVP trade-off.
"""
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common.parsing import json_body
from common.rate_limit import login_rate_limit, redeem_rate_limit
from .models import EmployeeAccessToken


@csrf_exempt
@login_rate_limit
def admin_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = json_body(request)
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
@redeem_rate_limit
def employee_redeem(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)
    data = json_body(request)
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


def auth_status(request):
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)
    admin = None
    employee = None
    if request.user.is_authenticated and request.user.is_staff:
        admin = {"username": request.user.username}
    emp_id = request.session.get("employee_id")
    emp_name = request.session.get("employee_name")
    if emp_id and emp_name:
        employee = {"id": emp_id, "name": emp_name}
    return JsonResponse({"admin": admin, "employee": employee})

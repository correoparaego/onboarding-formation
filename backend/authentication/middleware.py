"""Role-isolation middleware (spec authentication §Session Isolation).

Enforces that admin sessions and employee token sessions cannot cross into
each other's route namespaces:

- ``/api/admin/`` and ``/api/import``  -> require an admin (staff) session;
  an employee session hitting these returns 403.
- ``/api/employee/``                   -> require an employee token session;
  an admin session hitting these returns 403.
- ``/api/auth/`` and ``/api/health/``  -> public (login/logout/redeem/health).

Django's own ``/admin/`` is left to Django's auth; this middleware only
governs the JSON API surface introduced in Phase 3+.
"""
from django.http import JsonResponse

ADMIN_PREFIXES = (
    "/api/admin/",
    "/api/import",
    "/api/employees",
    "/api/courses/",
    "/api/course-versions/",
    "/api/sections/",
    "/api/positions/",
    "/api/banks/",
    "/api/ai/",
    "/api/certificate/",
    "/api/expediente/",
    "/api/audit",
)
EMPLOYEE_PREFIXES = ("/api/employee/", "/api/reading/", "/api/test/")
PUBLIC_PREFIXES = ("/api/auth/", "/api/health/")


class APICsrfeExemptionMiddleware:
    """Exempts all /api/ JSON endpoints from Django form-based CSRF checks.

    Security for API endpoints is handled via CORS_ALLOWED_ORIGINS and RoleIsolationMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/"):
            setattr(request, "_dont_enforce_csrf_checks", True)
        return self.get_response(request)


class RoleIsolationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Public auth + health are always reachable (login/logout/redeem/health).
        if any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES):
            return self.get_response(request)

        user = getattr(request, "user", None)
        is_admin = bool(
            user is not None
            and user.is_authenticated
            and getattr(user, "is_staff", False)
        )
        is_employee = bool(request.session.get("employee_id"))

        if any(path.startswith(prefix) for prefix in ADMIN_PREFIXES):
            if is_employee:
                return JsonResponse(
                    {"error": "employee session cannot access admin routes"},
                    status=403,
                )
            if not is_admin:
                return JsonResponse(
                    {"error": "admin authentication required"}, status=403
                )
            return self.get_response(request)

        if any(path.startswith(prefix) for prefix in EMPLOYEE_PREFIXES):
            if is_admin:
                return JsonResponse(
                    {"error": "admin session cannot access employee routes"},
                    status=403,
                )
            if not is_employee:
                return JsonResponse(
                    {"error": "employee authentication required"}, status=403
                )
            return self.get_response(request)

        # Any other path (e.g. future /api/* phases) is allowed through;
        # later phases tighten their own prefixes here.
        return self.get_response(request)

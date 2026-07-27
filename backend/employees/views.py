"""Employee Excel import (spec employee-import, Phase 4).

``POST /api/import`` (admin-only via RoleIsolationMiddleware) accepts an
.xlsx upload, parses rows, validates, and creates ``Employee`` records.

Key invariants (spec employee-import):
- DNI is stored VERBATIM — no trim, normalise, or case-fold. The raw cell
  string is passed straight to ``EncryptedDNIField``.
- A per-row validation report lists accepted/rejected rows with reasons
  (missing field, malformed email, invalid DNI format).
- Dedupe by DNI: a DNI already in the DB, or duplicated within the file, is
  flagged and never produces a second ``Employee`` (unique constraint holds).
- Idempotent: re-importing the same DNI creates nothing new.

Auto-enrollment (Phase 7) is intentionally NOT performed here; this endpoint
only creates Employee records + report.
"""
import io
import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import pandas as pd

from common.crypto import dni_lookup_hash
from common.dni import is_valid_dni
from reading_gate.services import assign_mandatory_courses

from .models import Employee

logger = logging.getLogger(__name__)

# Expected (case-insensitive, trimmed) header columns.
REQUIRED_FIELDS = ["dni", "name", "position", "email"]
OPTIONAL_FIELDS = ["phone"]


def _read_cell(row, key):
    value = row.get(key)
    # pandas uses NaN for empty cells when dtype coercion applies; we read
    # everything as str so only genuinely empty cells surface as None.
    if value is None:
        return None
    if isinstance(value, float) and value != value:  # NaN guard
        return None
    return str(value)


def _is_valid_email(value: str) -> bool:
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False


@csrf_exempt
def employee_import(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    upload = request.FILES.get("file")
    if not upload:
        return JsonResponse({"error": "file required"}, status=400)

    try:
        df = pd.read_excel(io.BytesIO(upload.read()), dtype=str)
    except Exception as exc:  # noqa: BLE001 - surface parse errors to admin
        return JsonResponse({"error": f"could not parse excel: {exc}"}, status=400)

    df.columns = [str(c).strip().lower() for c in df.columns]

    report = []
    created = 0
    duplicates = 0
    errors = 0
    enrollments_created = 0
    seen_in_file = set()

    for idx, row in df.iterrows():
        dni = _read_cell(row, "dni")
        name = _read_cell(row, "name")
        position = _read_cell(row, "position")
        email = _read_cell(row, "email")
        phone = _read_cell(row, "phone") or ""

        reasons = []
        if not dni:
            reasons.append("missing dni")
        if not name:
            reasons.append("missing name")
        if not position:
            reasons.append("missing position")
        if not email:
            reasons.append("missing email")
        elif not _is_valid_email(email):
            reasons.append("malformed email")
        # DNI format check only when present (else already reported missing).
        if dni and not is_valid_dni(dni):
            reasons.append("invalid DNI format")

        if reasons:
            errors += 1
            report.append(
                {
                    "row": int(idx) + 2,  # +1 header, +1 to 1-base
                    "status": "rejected",
                    "dni": dni,
                    "reasons": reasons,
                }
            )
            continue

        # Dedupe by DNI (verbatim, exact match).
        if dni in seen_in_file:
            duplicates += 1
            report.append(
                {
                    "row": int(idx) + 2,
                    "status": "duplicate",
                    "dni": dni,
                    "reasons": ["duplicate DNI in file"],
                }
            )
            continue
        if Employee.objects.filter(dni_lookup=dni_lookup_hash(dni)).exists():
            duplicates += 1
            report.append(
                {
                    "row": int(idx) + 2,
                    "status": "duplicate",
                    "dni": dni,
                    "reasons": ["DNI already exists"],
                }
            )
            continue

        # Store DNI VERBATIM — do NOT strip/upper/normalise.
        emp = Employee.objects.create(
            dni=dni,
            name=name,
            position=position,
            email=email,
            phone=phone,
        )
        seen_in_file.add(dni)
        created += 1
        # Audit: record the employee import (append-only; metadata only — NO DNI).
        try:
            from reading_gate import services as rg_services

            rg_services.audit_event(
                None,
                "import",
                "",
                "",
                {"employee_id": emp.id, "position": position, "status": "created"},
            )
        except Exception as exc:  # audit must never break import
            logger.warning("import audit failed: %s", exc)
        # Phase 7: auto-assign mandatory courses for the employee's position.
        # Idempotent by DNI+course (Enrollment.unique_together), so re-imports
        # of an already-enrolled employee create no duplicates.
        enrollments_created += assign_mandatory_courses(emp)
        report.append({"row": int(idx) + 2, "status": "created", "dni": dni})

    return JsonResponse(
        {
            "created": created,
            "duplicates": duplicates,
            "errors": errors,
            "enrollments_created": enrollments_created,
            "report": report,
        }
    )


def employee_list(request):
    """Admin-only list of all employees.

    GET /api/employees?limit=50&offset=0

    Returns paginated employee records for dashboard statistics.
    Admin-only via RoleIsolationMiddleware.
    """
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)

    qs = Employee.objects.all()
    total = qs.count()
    limit = min(int(request.GET.get("limit", 50)), 200)
    offset = int(request.GET.get("offset", 0))
    page = qs[offset : offset + limit]

    rows = [
        {
            "id": emp.id,
            "name": emp.name,
            "position": emp.position,
            "email": emp.email,
            "phone": emp.phone,
        }
        for emp in page
    ]
    return JsonResponse({"count": total, "limit": limit, "offset": offset, "results": rows})

"""Certificate PDF generation + badge award logic (spec certificate, badges)."""
import hashlib
import logging

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Badges (spec badges)
# ---------------------------------------------------------------------------
INITIAL_BADGES = [
    ("primer-curso", "Primer curso"),
    ("catalogo-completo", "Catálogo completo"),
    ("sin-fallos", "Sin fallos"),
]


def ensure_badges():
    """Idempotently create the initial badge set (defensive; migration also seeds)."""
    from certificates.models import Badge

    created = []
    for slug, label in INITIAL_BADGES:
        _, was = Badge.objects.get_or_create(slug=slug, defaults={"label": label})
        if was:
            created.append(slug)
    return created


def _positions_for_employee(employee):
    from courses.models import Position
    from django.utils.text import slugify

    positions = list(Position.objects.filter(name__iexact=employee.position))
    if not positions:
        positions = list(Position.objects.filter(slug__iexact=slugify(employee.position)))
    return positions


def award_badges_on_pass(enrollment):
    """Award the applicable initial badges when an enrollment passes.

    Idempotent via EmployeeBadge unique_together (spec badges §Award*).
    """
    from certificates.models import Badge, EmployeeBadge

    ensure_badges()
    employee = enrollment.employee
    awarded = []

    # Primer curso — employee's first passed course.
    passed_count = employee.enrollments.filter(status="passed").count()
    if passed_count == 1:
        badge, _ = Badge.objects.get_or_create(slug="primer-curso")
        _, was = EmployeeBadge.objects.get_or_create(employee=employee, badge=badge)
        if was:
            awarded.append("primer-curso")

    # Sin fallos — passed on the first attempt with no prior failures.
    if enrollment.attempts_used == 1:
        badge, _ = Badge.objects.get_or_create(slug="sin-fallos")
        _, was = EmployeeBadge.objects.get_or_create(employee=employee, badge=badge)
        if was:
            awarded.append("sin-fallos")

    # Catálogo completo — all mandatory courses for the position are passed.
    positions = _positions_for_employee(employee)
    if positions:
        from courses.models import Course

        mandatory = Course.objects.filter(position_catalog__in=positions).distinct()
        if mandatory.exists():
            all_passed = all(
                employee.enrollments.filter(course=c, status="passed").exists()
                for c in mandatory
            )
            if all_passed:
                badge, _ = Badge.objects.get_or_create(slug="catalogo-completo")
                _, was = EmployeeBadge.objects.get_or_create(
                    employee=employee, badge=badge
                )
                if was:
                    awarded.append("catalogo-completo")

    return awarded


# ---------------------------------------------------------------------------
# Certificate PDF (spec certificate) — reportlab imported lazily.
# ---------------------------------------------------------------------------
def _core_fields(enrollment):
    """Deterministic core fields used for the PDF and the regeneration hash."""
    employee = enrollment.employee
    course = enrollment.course
    score = None
    total = None
    try:
        from reading_gate.models import Expediente

        exp = Expediente.objects.filter(enrollment=enrollment).first()
        if exp:
            score = exp.score
            total = exp.total
    except Exception:
        pass
    sections = list(course.sections.order_by("order").values_list("order", flat=True))
    return {
        "employee_name": employee.name,
        "dni": employee.dni,  # verbatim — EncryptedDNIField decrypts to exact stored value
        "course_title": course.title,
        "score": score,
        "total": total,
        "sections": sections,
    }


def _core_hash(fields):
    payload = "|".join(
        [
            fields["employee_name"],
            fields["dni"],
            fields["course_title"],
            str(fields["score"]),
            str(fields["total"]),
            ",".join(str(s) for s in fields["sections"]),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_certificate_pdf(enrollment, issued_at=None):
    """Build a deterministic printable PDF (bytes). Requires reportlab."""
    import io

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    fields = _core_fields(enrollment)
    issued_date = issued_at or timezone.localdate()
    fields["issued_date"] = issued_date.isoformat()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 60 * mm, "CERTIFICADO DE FORMACIÓN")
    c.setFont("Helvetica", 12)
    y = height - 90 * mm
    c.drawString(25 * mm, y, f"Empleado/a: {fields['employee_name']}")
    y -= 8 * mm
    c.drawString(25 * mm, y, f"DNI: {fields['dni']}")  # verbatim, no formatting
    y -= 8 * mm
    c.drawString(25 * mm, y, f"Fecha: {fields['issued_date']}")
    y -= 8 * mm
    c.drawString(25 * mm, y, f"Curso: {fields['course_title']}")
    y -= 8 * mm
    eval_text = "No evaluado"
    if fields["score"] is not None:
        eval_text = f"{fields['score']} / {fields['total']} (apto)"
    c.drawString(25 * mm, y, f"Evaluación: {eval_text}")
    y -= 12 * mm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(25 * mm, y, "Índice resumen de la formación:")
    y -= 7 * mm
    c.setFont("Helvetica", 11)
    if fields["sections"]:
        for s in fields["sections"]:
            c.drawString(30 * mm, y, f"Sección {s}")
            y -= 6 * mm
    else:
        c.drawString(30 * mm, y, "Sin secciones registradas")
    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf, _core_hash(fields)

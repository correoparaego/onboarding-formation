"""Certificate PDF endpoint (admin-only via RoleIsolationMiddleware)."""
import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from certificates import services
from certificates.models import Certificate
from reading_gate.models import Enrollment

logger = logging.getLogger(__name__)


def certificate_pdf(request, pk):
    enrollment = get_object_or_404(
        Enrollment.objects.select_related("employee", "course"), pk=pk
    )
    if enrollment.status != "passed":
        return HttpResponse(
            '{"error":"certificate available only for passed enrollments"}',
            status=409,
            content_type="application/json",
        )
    cert, _ = Certificate.objects.get_or_create(enrollment=enrollment)
    pdf_bytes, core_hash = services.generate_certificate_pdf(
        enrollment, issued_at=cert.issued_at
    )
    cert.core_fields_hash = core_hash
    cert.save(update_fields=["core_fields_hash"])
    # Audit: record certificate issuance (append-only; metadata only — no DNI).
    try:
        from reading_gate import services as rg_services

        rg_services.audit_event(
            enrollment,
            "certificate_issued",
            "",
            "",
            {
                "course_title": enrollment.course.title,
                "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
            },
        )
    except Exception as exc:  # audit must never break cert delivery
        logger.warning("certificate audit failed: %s", exc)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="certificado_{enrollment.id}.pdf"'
    )
    return response

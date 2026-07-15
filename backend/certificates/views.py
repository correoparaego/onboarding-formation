"""Certificate PDF endpoint (admin-only via RoleIsolationMiddleware)."""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from certificates import services
from certificates.models import Certificate
from reading_gate.models import Enrollment


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
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="certificado_{enrollment.id}.pdf"'
    )
    return response

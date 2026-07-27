---
type: spec
resource: openspec/specs/certificate/spec.md
tags: [certificate, pdf, dni, verbatim, regeneration, compliance]
description: PDF certificate generation with employee data, course info, and result summary
status: active
generated: 2026-07-27
---

# Certificate

Generación de certificado PDF con datos del empleado, curso, y resultado.

## Requisitos clave

- **Printable PDF**: PDF con nombre completo, DNI, fecha, título curso, evaluación, summary index
- **DNI Verbatim**: DNI se imprime tal cual (sin formatear, sin añadir letra)
- **One Per Enrollment**: Máximo un certificado activo por enrollment pasado
- **Regeneration**: Regenerar reproduce mismo contenido (mismos campos core)
- **Result Data**: Certificado incluye datos de expediente (status, score, attempts)

## Relaciones

- Implementado en: [Backend Certificates](../backend/certificates.md)
- Relacionado: [Comprehension Test](../specs/comprehension-test.md) (pass → certificate trigger)
- Relacionado: [Expediente](../specs/expediente.md) (result data source)
- Relacionado: [Employee Import](../specs/employee-import.md) (DNI verbatim storage)
- Relacionado: [Audit Log](../specs/audit-log.md) (log certificate issuance)
- Frontend: [Admin](../frontend/admin.md) (admin downloads PDF)

## Decisiones de diseño

- RGPD assumption 2: printable PDF, NO e-signature (formal legal validity not required at MVP)
- DNI verbatim (no formatting) — stored as-is in employee record
- Certificate regeneration = same content (deterministic)
- Lazy import de reading_gate.services en certificates.views (audit events)

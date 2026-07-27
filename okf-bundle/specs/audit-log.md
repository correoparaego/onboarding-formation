---
type: spec
resource: openspec/specs/audit-log/spec.md
tags: [audit, log, append-only, immutable, compliance, rgpd, worm]
description: Append-only audit log for reading and exam events with device context
status: active
generated: 2026-07-27
---

# Audit Log

Audit log append-only para eventos de lectura y examen. Inmutable, con contexto de dispositivo.

## Requisitos clave

- **Append-Only**: Audit log solo permite append; NO edit, NO delete por application users
- **No Mutation**: Sistema rechaza cualquier update/delete en audit records
- **Cross-Device Context**: Cada evento registra device_id, session_id, timestamp, enrollment_id
- **Event Coverage**: Log mínimo: section unlock/complete, attempt start/submit/result, certificate issuance
- **Delivery Logging**: Notification delivery también se loggea (ver notifications)
- **Compliance Evidence**: Audit trail para mandatory training (idea.txt §8)

## Relaciones

- Implementado en: [Backend Reading Gate](../backend/reading_gate.md) (AuditEvent model, admin.py)
- Relacionado: [Timed Reading](../specs/timed-reading.md) (section unlock/complete events)
- Relacionado: [Comprehension Test](../specs/comprehension-test.md) (attempt events)
- Relacionado: [Certificate](../specs/certificate.md) (issuance events)
- Relacionado: [Notifications](../specs/notifications.md) (delivery logging)
- Relacionado: [Expediente](../specs/expediente.md) (both have retention requirements)

## Decisiones de diseño

- RGPD assumption 8: WORM only if mandated; MVP requires append-only immutability
- AuditEvent model: no create/update/delete API (solo append via services)
- Django admin: AuditEvent registered as read-only (no edit/delete buttons)
- Device context: device_id, session_id para cross-device evidence correlation
- Retention: audit records follow same retention policy as expediente

---
type: backend-module
resource: backend/reading_gate/
tags: [django, app, enrollment, reading, gate, heartbeat, audit, expediente, compliance]
description: Core compliance engine - enrollment, timed reading, comprehension test, audit, expediente
status: active
generated: 2026-07-27
---

# Reading Gate (Django App)

Core del sistema — motor de compliance para lectura cronometrada, tests, audit y expediente.

## Modelos

- **Enrollment**: Empleado + Curso, status, fechas
- **ReadingProgress**: Progress por enrollment (accumulated time, reached section)
- **AuditEvent**: Append-only log de eventos (section unlock, attempt, certificate)
- **Expediente**: Resultado por enrollment (status, attempts, score, dates)

## Services

- **process_heartbeat**: Heartbeat validation + time accumulation
- **check_gate**: Server-gated section unlock (minTimePerSection)
- **process_test_submission**: Test scoring + pass/fail + result storage
- **assign_mandatory_courses**: Auto-assignment post-import
- **generate_certificate**: Certificate PDF generation (lazy import a certificates.services)

## Relaciones

- Spec: [Timed Reading](../specs/timed-reading.md) (heartbeat, gate)
- Spec: [Comprehension Test](../specs/comprehension-test.md) (test submission)
- Spec: [Audit Log](../specs/audit-log.md) (AuditEvent)
- Spec: [Expediente](../specs/expediente.md) (Expediente model)
- Spec: [Enrollment Assignment](../specs/enrollment-assignment.md) (assign_mandatory_courses)
- Importado por: [Employees](../backend/employees.md) (views → assign_mandatory_courses)
- Importado por: [Certificates](../backend/certificates.md) (Enrollment, Expediente)
- Importado por: [Notifications](../backend/notifications.md) (Enrollment)
- Frontend: [Components](../frontend/components.md) (PdfReader heartbeat)

## Dependencias

- Importa: [Courses](../backend/courses.md) (Course, Section, Question, Position)
- Importa: [Employees](../backend/employees.md) (Employee model)
- Importa: [Common](../backend/common.md) (retention policy)
- Lazy imports: [Notifications](../backend/notifications.md), [Certificates](../backend/certificates.md) (evitar circular)

## Patrones clave

- Server-authoritative: todas las decisiones de gate se computan server-side
- Lazy imports para evitar circular dependencies
- AuditEvent: append-only, sin API de create/update/delete

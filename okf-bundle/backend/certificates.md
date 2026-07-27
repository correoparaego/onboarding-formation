---
type: backend-module
resource: backend/certificates/
tags: [django, app, certificate, badge, pdf, employee-badge]
description: Certificate PDF generation and badge award system
status: active
generated: 2026-07-27
---

# Certificates (Django App)

App Django para generación de certificados PDF y sistema de badges.

## Modelos

- **Certificate**: PDF generado por enrollment (one per passed enrollment)
- **Badge**: Definición de badge (nombre, descripción, criteria)
- **EmployeeBadge**: Badge otorgado a empleado (timestamp)

## Services

- **generate_certificate**: Genera PDF con datos del empleado, curso, resultado
- **award_badge**: Otorga badge a empleado si cumple criteria

## Relaciones

- Spec: [Certificate](../specs/certificate.md)
- Spec: [Badges](../specs/badges.md)
- Importado por: [Reading Gate](../backend/reading_gate.md) (lazy: services → generate_certificate, award_badge)
- Frontend: [Admin](../frontend/admin.md) (admin downloads PDF)

## Dependencias

- Importa: [Employees](../backend/employees.md) (Employee model)
- Importa: [Reading Gate](../backend/reading_gate.md) (Enrollment, Expediente)
- Importa: [Courses](../backend/courses.md) (Course lazy import)
- Lazy import en: [Reading Gate](../backend/reading_gate.md) (views → audit events)

## Patrones clave

- Lazy imports para evitar circular dependencies
- Certificate regeneration = deterministic (mismo contenido)
- Badge award automático (no manual)

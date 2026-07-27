---
type: spec
resource: openspec/specs/expediente/spec.md
tags: [expediente, result, retention, admin, filter, compliance]
description: Employee course result storage with admin filtering and retention policy
status: active
generated: 2026-07-27
---

# Expediente

Almacenamiento de resultados por enrollment con filtering admin y política de retención.

## Requisitos clave

- **Result Storage**: Expediente guarda status, attempts, score, dates por enrollment
- **Admin Filter**: Admin filtra empleados por completion de curso específico
- **Retention Policy**: Expediente se retiene según política (employee end + legal period)
- **Rollback Protection**: Expediente NO se purga en application rollback
- **Result Data Source**: Expediente es fuente de datos para certificados

## Relaciones

- Implementado en: [Backend Reading Gate](../backend/reading_gate.md) (Expediente model)
- Relacionado: [Comprehension Test](../specs/comprehension-test.md) (result → expediente)
- Relacionado: [Certificate](../specs/certificate.md) (expediente → certificate data)
- Relacionado: [Audit Log](../specs/audit-log.md) (both have retention requirements)
- Frontend: [Admin](../frontend/admin.md) (ExpedienteList, Dashboard)

## Decisiones de diseño

- Expediente linked to Employee + Course (composite key)
- Retention policy configurable en settings (EMPLOYEE_RETENTION_YEARS)
- Rollback protection: Expediente marked as protected (no cascade delete)
- Admin filter: queryset filtering por course completion status

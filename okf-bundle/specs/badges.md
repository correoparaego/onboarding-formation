---
type: spec
resource: openspec/specs/badges/spec.md
tags: [badge, award, gamification, recognition]
description: Badge system for employee achievement and recognition
status: active
generated: 2026-07-27
---

# Badges

Sistema de badges para reconocimiento de logros de empleados.

## Requisitos clave

- **Badge Definition**: Admin define badges (nombre, descripción, icon, criteria)
- **Automatic Award**: Badge se otorga automáticamente cuando empleado cumple criteria
- **Pass Trigger**: Pass de curso → award de badge asociado (si existe)
- **Employee Display**: Empleados ven sus badges en dashboard
- **Badge Criteria**: Criteria puede ser: pass specific course, pass N courses, score >= threshold

## Relaciones

- Implementado en: [Backend Certificates](../backend/certificates.md) (Badge, EmployeeBadge models)
- Relacionado: [Comprehension Test](../specs/comprehension-test.md) (pass → badge award)
- Relacionado: [Course Management](../specs/course-management.md) (course → badge mapping)
- Frontend: [Employee](../frontend/employee.md) (badge display en dashboard)

## Decisiones de diseño

- Badge award automático (no manual)
- Criteria evaluado server-side en certificates.services
- Lazy import en reading_gate.services (evitar circular dependency)
- EmployeeBadge tiene timestamp (cuándo se otorgó)

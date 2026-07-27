---
type: spec
resource: openspec/specs/enrollment-assignment/spec.md
tags: [enrollment, assignment, course, position, mandatory]
description: Automatic enrollment assignment based on employee position
status: active
generated: 2026-07-27
---

# Enrollment Assignment

Asignación automática de cursos obligatorios a empleados basada en su posición.

## Requisitos clave

- **Position-Course Mapping**: Cada posición tiene catálogo de cursos obligatorios
- **Auto-Assignment**: Al importar empleado, se asignan automáticamente cursos obligatorios
- **Mandatory Flag**: Cursos marcados como mandatory vs optional
- **Enrollment Creation**: Se crea Enrollment record por cada curso asignado

## Relaciones

- Implementado en: [Backend Reading Gate](../backend/reading_gate.md) (assign_mandatory_courses service)
- Relacionado: [Course Management](../specs/course-management.md) (Position model, Course-Position mapping)
- Relacionado: [Employee Import](../specs/employee-import.md) (trigger de auto-assignment)
- Relacionado: [Timed Reading](../specs/timed-reading.md) (enrollment → reading progress)

## Decisiones de diseño

- Assignment ocurre en employees.views (post-import)
- Llama a reading_gate.services.assign_mandatory_courses
- Idempotente: no duplica enrollments existentes

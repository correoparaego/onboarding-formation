---
type: feature
resource: backend/employees/models.py
tags: [employee, position, catalog, bulk-update]
description: Normalized current positions connect employees with mandatory course catalogs
status: active
generated: 2026-07-28
trust_tier: machine-confirmed
---

# Position Management

Conserva el texto importado y añade `current_position` como referencia normalizada. Permite cambios individuales y masivos.

## Relaciones

- Empleados: [Employees](../backend/employees.md)
- Cursos: [Courses](../backend/courses.md)
- Asignaciones: [Assignment Lifecycle](assignment-lifecycle.md)
- Importación: [Employee Import](../specs/employee-import.md)

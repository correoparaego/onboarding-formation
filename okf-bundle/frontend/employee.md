---
type: frontend-module
resource: frontend/src/employee/
tags: [react, employee, enrollment, pdf-reader, dashboard]
description: Employee portal - enrollment list, PDF reader, badges
status: active
generated: 2026-07-27
---

# Employee (Frontend)

Portal del empleado — lista de enrollments, lector PDF, badges.

## Archivos

- **EmployeeApp.tsx**: Router employee con enrollment list + PDF reader route

## Relaciones

- Spec: [Timed Reading](../specs/timed-reading.md) (PDF reader con heartbeat)
- Spec: [Badges](../specs/badges.md) (badge display)
- Backend: [Reading Gate](../backend/reading_gate.md) (enrollment, heartbeat)
- Frontend: [Auth](../frontend/auth.md) (ProtectedRoute)
- Frontend: [Components](../frontend/components.md) (PdfReader)

## Dependencias

- Importa: [Auth](../frontend/auth.md) (ProtectedRoute, AuthContext)
- Importa: [API](../frontend/api.md) (client)
- Importa: [Components](../frontend/components.md) (PdfReader, UI)

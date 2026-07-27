---
type: frontend-module
resource: frontend/src/api/
tags: [react, api, axios, client, endpoints, interceptor]
description: API layer - Axios client with auth interceptor and typed endpoints
status: active
generated: 2026-07-27
---

# API (Frontend)

Capa de API — cliente Axios con interceptor de auth y endpoints tipados.

## Archivos

- **client.ts**: Instancia Axios con interceptor (redirect a login si 401)
- **endpoints.ts**: Funciones API tipadas (auth, import, courses, banks, AI)

## Relaciones

- Backend: [Authentication](../backend/authentication.md), [Employees](../backend/employees.md), [Courses](../backend/courses.md), [AI Generation](../backend/ai_generation.md)
- Usado por: [Auth](../frontend/auth.md) (AuthContext, AdminLogin, EmployeeRedeem)
- Usado por: [Admin](../frontend/admin.md) (Dashboard, EmployeeImport, CourseManagement, AI pages)
- Usado por: [Employee](../frontend/employee.md) (EmployeeApp)

## Patrones clave

- Axios interceptor: redirect a login si 401
- Endpoints tipados con TypeScript
- Cliente compartido (single Axios instance)

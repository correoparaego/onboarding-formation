---
type: frontend-module
resource: frontend/src/auth/
tags: [react, auth, context, login, redeem, protected-route]
description: Auth context, admin login, employee redeem, protected routes
status: active
generated: 2026-07-27
---

# Auth (Frontend)

Capa de autenticación del frontend — contexto, formularios, y route guards.

## Archivos

- **AuthContext.tsx**: Context provider con estado auth (admin/employee), login/logout/redeem
- **AdminLogin.tsx**: Formulario de login admin (username/password)
- **EmployeeRedeem.tsx**: Formulario de redeem employee (código/token)
- **ProtectedRoute.tsx**: Route guard por rol (admin/employee)

## Relaciones

- Spec: [Authentication](../specs/authentication.md)
- Spec: [Secure Access](../specs/secure-access.md)
- Backend: [Authentication](../backend/authentication.md) (API calls)
- Frontend: [API](../frontend/api.md) (auth endpoints)
- Usado por: [Admin](../frontend/admin.md) (AdminApp wraps with ProtectedRoute)
- Usado por: [Employee](../frontend/employee.md) (EmployeeApp wraps with ProtectedRoute)

## Dependencias

- Importa: [API](../frontend/api.md) (auth endpoints)
- Importa: [Components](../frontend/components.md) (UI primitives)
- Importa: ToastContext (notifications)

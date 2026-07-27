---
type: backend-module
resource: backend/authentication/
tags: [django, app, auth, session, token, employee-access, admin-login, middleware]
description: Admin login/logout, employee access token, role isolation middleware
status: active
generated: 2026-07-27
---

# Authentication (Django App)

App Django para autenticación admin (session) y employee (token), con middleware de aislamiento.

## Modelos

- **EmployeeAccessToken**: Token de acceso para empleados (cifrado, un solo uso, expirable)

## Views/APIs

- Admin login (POST /api/auth/login)
- Admin logout (POST /api/auth/logout)
- Employee redeem (POST /api/auth/redeem)

## Middleware

- **RoleIsolationMiddleware**: Aísla sesiones admin/employee; employee token NO concede acceso admin

## Relaciones

- Spec: [Authentication](../specs/authentication.md)
- Spec: [Secure Access](../specs/secure-access.md) (EmployeeAccessToken)
- Importado por: [Notifications](../backend/notifications.md) (EmployeeAccessToken)
- Frontend: [Auth](../frontend/auth.md) (AdminLogin, EmployeeRedeem, AuthContext)

## Dependencias

- Importa: [Employees](../backend/employees.md) (Employee model)
- Importa: [Common](../backend/common.md) (parsing, rate_limit utilities)
- No tiene circular dependencies

## Patrones clave

- Django session para admin (no JWT)
- Token cifrado con AES-GCM + random nonce
- HMAC para dedup determinístico
- Raw token NUNCA en serialized responses
- Middleware enforce role isolation en cada request

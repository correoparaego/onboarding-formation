---
type: spec
resource: openspec/specs/authentication/spec.md
tags: [auth, security, session, rgpd, admin, employee]
description: Admin password session + employee magic-link authentication with role isolation
status: active
generated: 2026-07-27
---

# Authentication

Admin login/logout con server-side session (Django session). Employee access via magic-link/code token sin password.

## Requisitos clave

- **Admin Password Session**: Admins se autentican con username/password y mantienen sesión server-side
- **Employee Magic-Link**: Empleados acceden solo con token/magic-link emitido (sin password)
- **Session Isolation**: Sesiones admin y employee están aisladas; token employee NO concede acceso admin
- **Admin Logout**: Logout invalida sesión server-side

## Relaciones

- Implementado en: [Backend Authentication](../backend/authentication.md)
- Relacionado: [Secure Access](../specs/secure-access.md) (emisión de tokens employee)
- Relacionado: [Notifications](../specs/notifications.md) (envío de magic-link)
- Frontend: [Auth](../frontend/auth.md) (AdminLogin, EmployeeRedeem)

## Decisiones de diseño

- RGPD assumption 4: email possession ≈ identity para MVP
- Weak binding aceptada, flagged para phase-2 strengthening
- Server-side session para admin (no JWT)

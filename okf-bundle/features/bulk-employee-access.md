---
type: feature
resource: backend/notifications/views.py
tags: [employee, access-code, batch, notification, no-store]
description: Administrators generate and deliver one-time employee access credentials in controlled batches
status: active
generated: 2026-07-28
trust_tier: machine-confirmed
---

# Bulk Employee Access

Genera o rota credenciales temporales para lotes de empleados, permite copia administrativa y evita cachear la respuesta sensible.

## Relaciones

- Notificaciones: [Notifications](../backend/notifications.md)
- Autenticación: [Authentication](../backend/authentication.md)
- Matrículas: [Assignment Lifecycle](assignment-lifecycle.md)
- Acceso seguro: [Secure Access](../specs/secure-access.md)

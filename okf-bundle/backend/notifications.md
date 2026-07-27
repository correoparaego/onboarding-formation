---
type: backend-module
resource: backend/notifications/
tags: [django, app, notification, email, transport, template, spanish]
description: Email notification system with configurable transport and Spanish templates
status: active
generated: 2026-07-27
---

# Notifications (Django App)

App Django para notificaciones email con transporte configurable y templates en español.

## Modelos

- **NotificationLog**: Log de notificaciones enviadas (recipient, status, timestamp)

## Services

- **send_notification**: Envía email via transporte configurado (console/smtp/resend)
- **send_token_email**: Envía magic-link/token a empleado

## Transports

- **Console**: Para desarrollo (print to stdout)
- **SMTP**: Para producción genérica
- **Resend**: Para producción (API-based)

## Relaciones

- Spec: [Notifications](../specs/notifications.md)
- Spec: [Secure Access](../specs/secure-access.md) (token delivery)
- Importado por: [Reading Gate](../backend/reading_gate.md) (lazy: services → send_notification)
- Importado por: [Authentication](../backend/authentication.md) (EmployeeAccessToken referenced)

## Dependencias

- Importa: [Authentication](../backend/authentication.md) (EmployeeAccessToken)
- Importa: [Reading Gate](../backend/reading_gate.md) (Enrollment en views)
- No tiene circular dependencies

## Patrones clave

- Email transport abstraction (configurable en settings)
- Templates hardcoded en español (no i18n para MVP)
- NotificationLog append-only (evidence trail)

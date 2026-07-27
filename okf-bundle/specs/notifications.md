---
type: spec
resource: openspec/specs/notifications/spec.md
tags: [notifications, email, transport, template, spanish, delivery]
description: Email notification system with configurable transport and Spanish templates
status: active
generated: 2026-07-27
---

# Notifications

Sistema de notificaciones email con transporte configurable y templates en español.

## Requisitos clave

- **Configurable Transport**: Console (dev), SMTP, Resend (prod) — configurable via settings
- **Spanish Templates**: Todos los templates en español (RGPD assumption — usuarios españoles)
- **Delivery Logging**: NotificationLog persiste status (sent/failed), timestamp, recipient
- **Token Delivery**: Envío de magic-link/token a empleados (ver secure-access)
- **No Opt-Out**: Mandatory training notifications no tienen opt-out (compliance)

## Relaciones

- Implementado en: [Backend Notifications](../backend/notifications.md)
- Relacionado: [Secure Access](../specs/secure-access.md) (token delivery)
- Relacionado: [Authentication](../specs/authentication.md) (employee magic-link)
- Relacionado: [Audit Log](../specs/audit-log.md) (delivery logging)

## Decisiones de diseño

- Email transport abstraction (console/smtp/resend)
- Templates hardcoded en español (no i18n para MVP)
- NotificationLog append-only (evidence trail)
- Lazy import en reading_gate.services (evitar circular dependency)

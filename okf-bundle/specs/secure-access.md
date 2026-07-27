---
type: spec
resource: openspec/specs/secure-access/spec.md
tags: [security, token, magic-link, employee, rgpd]
description: Employee access token generation, delivery, and redemption
status: active
generated: 2026-07-27
---

# Secure Access

Emisión y redención de tokens de acceso para empleados. Un solo uso, expiración configurable.

## Requisitos clave

- **Token Generation**: Generar token único por empleado, cifrado en BD
- **Token Delivery**: Enviar magic-link por email (ver notifications)
- **Token Redemption**: Validar token no usado, autenticar empleado, marcar como usado
- **Expiration**: Tokens expiran tras tiempo configurable o primer uso

## Relaciones

- Implementado en: [Backend Authentication](../backend/authentication.md) (EmployeeAccessToken model)
- Relacionado: [Authentication](../specs/authentication.md) (sesión employee post-redención)
- Relacionado: [Notifications](../specs/notifications.md) (envío de token)
- Frontend: [Auth](../frontend/auth.md) (EmployeeRedeem component)

## Decisiones de diseño

- Token cifrado con AES-GCM + nonce aleatorio
- HMAC separado para deduplicación determinística
- Raw token NUNCA se loggea o expone en respuestas

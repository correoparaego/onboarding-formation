---
type: security
resource: backend/mvp_project/settings.py
tags: [session, csrf, cors, aes-gcm, hmac, token, authorization, secrets]
description: Session authentication, one-time employee access, encrypted DNI, CSRF, and private content boundaries
status: active
generated: 2026-07-28
trust_tier: human-reviewed
---

# Security Model

Administradores usan sesión Django; empleados canjean credenciales temporales. El DNI usa AES-GCM y lookup HMAC. CSRF protege mutaciones generales y los PDFs requieren ownership.

## Relaciones

- Auth: [Authentication](../backend/authentication.md)
- Criptografía: [Common](../backend/common.md)
- Acceso: [Secure Access](../specs/secure-access.md)
- Infraestructura: [Render Deployment](../deployment/render.md)
- Deuda: [Production Readiness](../risks/production-readiness.md)

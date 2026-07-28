---
type: architecture
resource: Dockerfile
tags: [react, django, nginx, gunicorn, postgres, render, monolith]
description: React and Django run as a same-origin modular monolith inside one Render Docker service
status: active
generated: 2026-07-28
trust_tier: human-reviewed
---

# System Architecture

Nginx sirve la SPA y delega `/api/` y `/django-admin/` en Gunicorn/Django. PostgreSQL persiste dominio y S3 opcional conserva PDFs privados.

## Relaciones

- Proyecto: [Onboarding Formation](../project/overview.md)
- Backend: [Reading Gate](../backend/reading_gate.md)
- Frontend: [Admin](../frontend/admin.md)
- Despliegue: [Render Deployment](../deployment/render.md)
- Seguridad: [Security Model](../security/security-model.md)

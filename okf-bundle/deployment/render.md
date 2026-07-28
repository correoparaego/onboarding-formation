---
type: deployment
resource: render.yaml
tags: [render, docker, frankfurt, nginx, gunicorn, postgres, s3, resend]
description: One Docker Web Service in Render Frankfurt with external PostgreSQL and optional S3 storage
status: active
generated: 2026-07-28
trust_tier: machine-confirmed
---

# Render Deployment

`render.yaml` despliega un Web Service Docker por commit. El contenedor compila React, ejecuta migraciones y arranca Gunicorn detrás de Nginx.

## Relaciones

- Arquitectura: [System Architecture](../architecture/system.md)
- PDFs: [Private Section PDFs](../features/private-section-pdfs.md)
- Seguridad: [Security Model](../security/security-model.md)
- Calidad: [Testing and Quality](../quality/testing.md)
- Riesgos: [Production Readiness](../risks/production-readiness.md)

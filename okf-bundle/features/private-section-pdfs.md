---
type: feature
resource: backend/reading_gate/views.py
tags: [pdf, private-storage, s3, authorization, section]
description: Section PDFs are stored privately and streamed only through authorized enrollment routes
status: active
generated: 2026-07-28
trust_tier: machine-confirmed
---

# Private Section PDFs

Los PDFs se validan, almacenan mediante Django Storage y se entregan con autorización por matrícula y sección desbloqueada. `/media/` no constituye una ruta pública.

## Relaciones

- Modelo de contenido: [Courses](../backend/courses.md)
- Control de lectura: [Timed Reading](../specs/timed-reading.md)
- Infraestructura: [Render Deployment](../deployment/render.md)
- Seguridad: [Security Model](../security/security-model.md)

---
type: feature
resource: backend/courses/models.py
tags: [course, version, draft, published, archived, history]
description: Immutable course versions preserve the exact content assigned to each enrollment
status: active
generated: 2026-07-28
trust_tier: machine-confirmed
---

# Course Versioning

`Course` conserva la identidad estable; `CourseVersion` contiene el snapshot publicable. Cada matrícula referencia una versión para impedir cambios retrospectivos.

## Relaciones

- Implementación: [Courses](../backend/courses.md)
- Orquestación: [Assignment Lifecycle](assignment-lifecycle.md)
- Contenido: [Private Section PDFs](private-section-pdfs.md)
- Especificación original: [Course Management](../specs/course-management.md)
- Riesgos históricos: [Production Readiness](../risks/production-readiness.md)

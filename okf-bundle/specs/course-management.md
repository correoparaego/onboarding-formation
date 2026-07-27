---
type: spec
resource: openspec/specs/course-management/spec.md
tags: [course, section, question, position, catalog, admin]
description: Course CRUD with sections, question banks, and position mapping
status: active
generated: 2026-07-27
---

# Course Management

CRUD de cursos con secciones, question banks, y mapeo a posiciones.

## Requisitos clave

- **Course CRUD**: Admin crea/edita cursos con título, descripción, metadata
- **Section Management**: Cursos tienen secciones (PDFs) con orden y minTimePerSection
- **Question Bank**: Banco de preguntas por curso (multiple choice, single correct)
- **Position Mapping**: Mapeo N:M entre cursos y posiciones (catálogo obligatorio)
- **HITL for AI**: Contenido generado por AI requiere revisión/explicit save del admin

## Relaciones

- Implementado en: [Backend Courses](../backend/courses.md)
- Relacionado: [AI Generation](../specs/ai-generation.md) (generación de contenido/tests)
- Relacionado: [Enrollment Assignment](../specs/enrollment-assignment.md) (Position-Course mapping)
- Relacionado: [Timed Reading](../specs/timed-reading.md) (sections con minTime)
- Relacionado: [Comprehension Test](../specs/comprehension-test.md) (question bank)
- Frontend: [Admin](../frontend/admin.md) (CourseManagement component)

## Decisiones de diseño

- Question tiene Position (orden dentro de bank)
- Single correct answer por question (spec comprehension-test §Single Correct)
- AI-generated content NO se persiste automáticamente (HITL)

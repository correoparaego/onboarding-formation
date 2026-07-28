---
type: backend-module
resource: backend/courses/
tags: [django, app, course, versioning, section, question, position, catalog, private-pdf]
description: Versioned courses, sections, question banks, positions, publication lifecycle, and private PDFs
status: active
generated: 2026-07-28
---

# Courses (Django App)

App Django para gestión de cursos, secciones, preguntas y posiciones.

## Modelos

- **Course**: Identidad estable, catálogo por puestos y referencia a versión activa
- **CourseVersion**: Snapshot draft/published/archived fijado a las matrículas
- **Section**: Contenido y PDF privado dentro de una versión, con orden y tiempo base
- **Question**: Preguntas del question bank (single correct answer)
- **QuestionBank**: Contenedor de preguntas por curso
- **Position**: Posiciones de trabajo (mapeo N:M con cursos)

## Views/APIs

- Course CRUD (admin-only)
- Section management
- Question bank management
- Position-catalog listing
- Version clone, publish, archive, and active-version lifecycle
- Authenticated section PDF upload and delivery

## Relaciones

- Spec: [Course Management](../specs/course-management.md)
- Spec: [Comprehension Test](../specs/comprehension-test.md) (Question model)
- Spec: [Timed Reading](../specs/timed-reading.md) (Section model)
- Spec: [Enrollment Assignment](../specs/enrollment-assignment.md) (Position model)
- Importado por: [Reading Gate](../backend/reading_gate.md) (Course, Section, Question, Position)
- Importado por: [Certificates](../backend/certificates.md) (Course lazy import)
- Frontend: [Admin](../frontend/admin.md) (CourseManagement component)
- Feature: [Course Versioning](../features/course-versioning.md)
- Feature: [Private Section PDFs](../features/private-section-pdfs.md)

## Dependencias

- Importa: [Common](../backend/common.md) (parsing utilities)
- No tiene dependencias circulares

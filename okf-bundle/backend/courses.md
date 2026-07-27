---
type: backend-module
resource: backend/courses/
tags: [django, app, course, section, question, position, catalog]
description: Course, Section, Question, QuestionBank, Position models and CRUD views
status: active
generated: 2026-07-27
---

# Courses (Django App)

App Django para gestión de cursos, secciones, preguntas y posiciones.

## Modelos

- **Course**: Título, descripción, metadata del curso
- **Section**: PDFs dentro de un curso, con orden y minTimePerSection
- **Question**: Preguntas del question bank (single correct answer)
- **QuestionBank**: Contenedor de preguntas por curso
- **Position**: Posiciones de trabajo (mapeo N:M con cursos)

## Views/APIs

- Course CRUD (admin-only)
- Section management
- Question bank management
- Position-catalog listing

## Relaciones

- Spec: [Course Management](../specs/course-management.md)
- Spec: [Comprehension Test](../specs/comprehension-test.md) (Question model)
- Spec: [Timed Reading](../specs/timed-reading.md) (Section model)
- Spec: [Enrollment Assignment](../specs/enrollment-assignment.md) (Position model)
- Importado por: [Reading Gate](../backend/reading_gate.md) (Course, Section, Question, Position)
- Importado por: [Certificates](../backend/certificates.md) (Course lazy import)
- Frontend: [Admin](../frontend/admin.md) (CourseManagement component)

## Dependencias

- Importa: [Common](../backend/common.md) (parsing utilities)
- No tiene dependencias circulares

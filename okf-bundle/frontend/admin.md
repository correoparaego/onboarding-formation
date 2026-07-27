---
type: frontend-module
resource: frontend/src/admin/
tags: [react, admin, dashboard, import, course, expediente, ai, lazy]
description: Admin panel - dashboard, employee import, course management, expediente, AI pages
status: active
generated: 2026-07-27
---

# Admin (Frontend)

Panel de administración — dashboard, import, gestión de cursos, expediente, y páginas AI (lazy-loaded).

## Archivos

- **AdminApp.tsx**: Router admin (lazy-loads AI pages)
- **Dashboard.tsx**: Charts (recharts) para expedientes
- **EmployeeImport.tsx**: Excel upload + reporte de importación
- **CourseManagement.tsx**: CRUD de cursos + question bank
- **ExpedienteList.tsx**: Tabla filtrable/paginated de expedientes

### AI Pages (lazy-loaded via React.lazy)
- **ai/AiKeyForm.tsx**: Formulario BYO LLM key (react-hook-form + zod)
- **ai/GuidedContent.tsx**: Generación guiada de contenido + auto-save
- **ai/PdfTestGen.tsx**: Generación de tests desde PDF

## Relaciones

- Spec: [Course Management](../specs/course-management.md)
- Spec: [Employee Import](../specs/employee-import.md)
- Spec: [Expediente](../specs/expediente.md)
- Spec: [AI Generation](../specs/ai-generation.md)
- Backend: [Courses](../backend/courses.md), [Employees](../backend/employees.md), [Reading Gate](../backend/reading_gate.md), [AI Generation](../backend/ai_generation.md)
- Frontend: [Auth](../frontend/auth.md) (ProtectedRoute)
- Frontend: [Components](../frontend/components.md) (layout, UI)

## Dependencias

- Importa: [Auth](../frontend/auth.md) (ProtectedRoute, AuthContext)
- Importa: [API](../frontend/api.md) (endpoints)
- Importa: [Components](../frontend/components.md) (layout, UI primitives)
- Importa: ToastContext, ThemeContext

## Patrones clave

- AI pages lazy-loaded (code-split via React.lazy)
- Dashboard usa recharts para gráficos
- react-hook-form + zod para validación de formularios

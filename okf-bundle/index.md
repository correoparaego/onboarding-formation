---
type: index
description: Onboarding Formation - Knowledge Graph Root
generated: 2026-07-28
status: active
---

# Onboarding Formation

Sistema de onboarding y formación corporativa con cumplimiento RGPD.

## Arquitectura

- **Backend**: Django REST Framework con 7 apps + módulo common
- **Frontend**: React 18 + TypeScript + Vite
- **Base de datos**: PostgreSQL (producción) / SQLite (desarrollo)

## Dominio

El sistema gestiona:
1. Importación y gestión de empleados y puestos
2. Versionado de cursos y PDFs privados por sección
3. Asignación automática, manual y por ciclos
4. Acceso individual o masivo mediante credenciales temporales
5. Lectura cronometrada con gate server-side
6. Tests, expediente, badges, certificados y auditoría
7. Autoría asistida por IA con revisión humana
8. Despliegue monolítico Docker en Render

## Navegación

### Especificaciones
- [Authentication](specs/authentication.md)
- [Secure Access](specs/secure-access.md)
- [Employee Import](specs/employee-import.md)
- [Enrollment Assignment](specs/enrollment-assignment.md)
- [Course Management](specs/course-management.md)
- [AI Generation](specs/ai-generation.md)
- [Timed Reading](specs/timed-reading.md)
- [Comprehension Test](specs/comprehension-test.md)
- [Notifications](specs/notifications.md)
- [Certificate](specs/certificate.md)
- [Badges](specs/badges.md)
- [Expediente](specs/expediente.md)
- [Audit Log](specs/audit-log.md)

### Backend
- [Courses](backend/courses.md)
- [Employees](backend/employees.md)
- [Reading Gate](backend/reading_gate.md)
- [Certificates](backend/certificates.md)
- [Notifications](backend/notifications.md)
- [Authentication](backend/authentication.md)
- [AI Generation](backend/ai_generation.md)
- [Common](backend/common.md)

### Frontend
- [Auth](frontend/auth.md)
- [Admin](frontend/admin.md)
- [Employee](frontend/employee.md)
- [Components](frontend/components.md)
- [API](frontend/api.md)

### Capacidades y operación actuales

- [Project Overview](project/overview.md)
- [Course Versioning](features/course-versioning.md)
- [Assignment Lifecycle](features/assignment-lifecycle.md)
- [Position Management](features/position-management.md)
- [Private Section PDFs](features/private-section-pdfs.md)
- [Bulk Employee Access](features/bulk-employee-access.md)
- [System Architecture](architecture/system.md)
- [Render Deployment](deployment/render.md)
- [Security Model](security/security-model.md)
- [Testing and Quality](quality/testing.md)
- [Git and Pull Requests](git/history.md)
- [Production Readiness](risks/production-readiness.md)
- [Technical Documentation](documentation/technical-documentation.md)

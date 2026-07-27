---
type: index
description: Onboarding Formation - Knowledge Graph Root
generated: 2026-07-27
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
1. Importación de empleados desde Excel
2. Asignación automática de cursos obligatorios por posición
3. Lectura cronometrada con gate server-side
4. Tests de comprensión con límite de intentos
5. Generación de certificados PDF
6. Badges y expediente académico
7. Audit log inmutable para compliance

## Navegación

### Especificaciones
- [Authentication](../specs/authentication.md)
- [Secure Access](../specs/secure-access.md)
- [Employee Import](../specs/employee-import.md)
- [Enrollment Assignment](../specs/enrollment-assignment.md)
- [Course Management](../specs/course-management.md)
- [AI Generation](../specs/ai-generation.md)
- [Timed Reading](../specs/timed-reading.md)
- [Comprehension Test](../specs/comprehension-test.md)
- [Notifications](../specs/notifications.md)
- [Certificate](../specs/certificate.md)
- [Badges](../specs/badges.md)
- [Expediente](../specs/expediente.md)
- [Audit Log](../specs/audit-log.md)

### Backend
- [Courses](../backend/courses.md)
- [Employees](../backend/employees.md)
- [Reading Gate](../backend/reading_gate.md)
- [Certificates](../backend/certificates.md)
- [Notifications](../backend/notifications.md)
- [Authentication](../backend/authentication.md)
- [AI Generation](../backend/ai_generation.md)
- [Common](../backend/common.md)

### Frontend
- [Auth](../frontend/auth.md)
- [Admin](../frontend/admin.md)
- [Employee](../frontend/employee.md)
- [Components](../frontend/components.md)
- [API](../frontend/api.md)

---
type: backend-module
resource: backend/employees/
tags: [django, app, employee, dni, encryption, import, excel]
description: Employee model with encrypted DNI and Excel import
status: active
generated: 2026-07-27
---

# Employees (Django App)

App Django para gestión de empleados con cifrado DNI y importación Excel.

## Modelos

- **Employee**: Nombre, email, DNI cifrado (AES-GCM), HMAC lookup, posición

## Views/APIs

- Employee Excel import (POST /api/import)
- Employee listing

## Relaciones

- Spec: [Employee Import](../specs/employee-import.md)
- Spec: [Secure Access](../specs/secure-access.md) (Employee referenced by token)
- Importado por: [Authentication](../backend/authentication.md) (Employee model)
- Importado por: [Reading Gate](../backend/reading_gate.md) (Employee model)
- Importado por: [Certificates](../backend/certificates.md) (Employee model)
- Frontend: [Admin](../frontend/admin.md) (EmployeeImport component)

## Dependencias

- Importa: [Common](../backend/common.md) (crypto, fields, dni utilities)
- Importa: [Reading Gate](../backend/reading_gate.md) (assign_mandatory_courses en views)

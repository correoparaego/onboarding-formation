---
type: spec
resource: openspec/specs/employee-import/spec.md
tags: [import, excel, employee, dni, encryption, rgpd]
description: Excel import of employees with DNI encryption and deduplication
status: active
generated: 2026-07-27
---

# Employee Import

Importación masiva de empleados desde Excel con validación, cifrado DNI y deduplicación.

## Requisitos clave

- **Excel Upload**: Admin sube archivo .xlsx con columnas: nombre, email, DNI, posición
- **DNI Encryption**: DNI se cifra con AES-GCM antes de persistir (non-deterministic)
- **DNI Dedup**: HMAC determinístico para detectar DNI duplicados sin exponer valor
- **Validation Report**: Report de errores (filas inválidas, duplicados, DNI inválido)
- **Verbatim Storage**: DNI se guarda tal cual (sin formatear) para certificados

## Relaciones

- Implementado en: [Backend Employees](../backend/employees.md)
- Relacionado: [Common](../backend/common.md) (crypto, fields, dni utilities)
- Relacionado: [Enrollment Assignment](../specs/enrollment-assignment.md) (asignación automática post-import)
- Frontend: [Admin](../frontend/admin.md) (EmployeeImport component)

## Decisiones de diseño

- DNI verbatim en certificado (sin formatear)
- Cifrado non-deterministic (AES-GCM + random nonce)
- HMAC para lookup/dedup sin exponer DNI plaintext
- RGPD: right to erasure requiere delete de ciphertext + HMAC

---
type: backend-module
resource: backend/common/
tags: [django, utility, crypto, dni, encryption, parsing, rate-limit, retention]
description: Shared utilities - crypto, DNI fields, parsing, rate limiting, retention policy
status: active
generated: 2026-07-27
---

# Common (Utility Package)

Package compartido con utilidades transversales (no es Django app, es módulo Python).

## Módulos

- **crypto.py**: AES-GCM encryption/decryption, key derivation, HMAC
- **fields.py**: EncryptedDNIField, HashedDNILookupField (Django model fields)
- **dni.py**: DNI validation (formato español + control letter)
- **parsing.py**: JSON body parsing utilities
- **rate_limit.py**: Rate limiting decorator
- **retention.py**: Retention policy configuration

## Relaciones

- Importado por: [Employees](../backend/employees.md) (crypto, fields, dni)
- Importado por: [Authentication](../backend/authentication.md) (parsing, rate_limit)
- Importado por: [Reading Gate](../backend/reading_gate.md) (retention)
- Importado por: [AI Generation](../backend/ai_generation.md) (crypto)
- Importado por: [Courses](../backend/courses.md) (parsing)
- Spec: [Employee Import](../specs/employee-import.md) (DNI utilities)
- Spec: [AI Generation](../specs/ai-generation.md) (crypto para key encryption)

## Patrones clave

- Leaf module: no importa de otras apps del proyecto
- EncryptedDNIField: AES-GCM + random nonce (non-deterministic ciphertext)
- HashedDNILookupField: HMAC para dedup sin exponer plaintext
- Retention policy configurable via settings

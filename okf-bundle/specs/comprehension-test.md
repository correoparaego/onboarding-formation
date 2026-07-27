---
type: spec
resource: openspec/specs/comprehension-test/spec.md
tags: [test, comprehension, question, attempt, score, pass]
description: Comprehension test with attempt limits, scoring, and pass/fail logic
status: active
generated: 2026-07-27
---

# Comprehension Test

Test de comprensión post-reading con límite de intentos, scoring, y pass/fail.

## Requisitos clave

- **Test Unlock**: Test se habilita solo cuando reading está completo (todas secciones pasan gate)
- **Question Bank**: Preguntas del curso (single correct answer por spec course-management §Single Correct)
- **Attempt Limit**: Máximo de intentos configurable por curso
- **Scoring**: Score = preguntas correctas / total preguntas
- **Pass Threshold**: Threshold configurable (ej. 70%)
- **Result Storage**: Resultado (status, attempts, score) se guarda en expediente
- **Certificate Trigger**: Pass → habilita generación de certificado

## Relaciones

- Implementado en: [Backend Reading Gate](../backend/reading_gate.md) (services.py: process_test_submission)
- Relacionado: [Timed Reading](../specs/timed-reading.md) (test unlock post-reading)
- Relacionado: [Course Management](../specs/course-management.md) (Question model, question bank)
- Relacionado: [Certificate](../specs/certificate.md) (pass → certificate generation)
- Relacionado: [Badges](../specs/badges.md) (pass → badge award)
- Relacionado: [Expediente](../specs/expediente.md) (result storage)
- Relacionado: [Audit Log](../specs/audit-log.md) (log attempt start/submit/result)

## Decisiones de diseño

- Single correct answer (no partial credit)
- Attempt limit hard (no más intentos tras agotar)
- Score calculado server-side (client NO envía score)
- Result inmutable post-submission

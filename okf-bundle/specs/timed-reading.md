---
type: spec
resource: openspec/specs/timed-reading/spec.md
tags: [reading, gate, heartbeat, time, compliance, server-authority]
description: Server-gated reading time enforcement with heartbeat validation
status: active
generated: 2026-07-27
---

# Timed Reading

Gate server-side para tiempo de lectura. Secciones no se desbloquean hasta acumular minTime.

## Requisitos clave

- **Server-Gated Unlock**: Sección NO se marca completa hasta server valida active time >= minTimePerSection
- **minTimePerSection**: `sectionBase / 3` (configurable por curso)
- **Heartbeat Validation**: Cliente envía heartbeats de actividad; server valida y acumula tiempo
- **Active-Time Only**: Solo se acredita tiempo con heartbeats válidos (gap detection)
- **Cross-Device Resume**: Persistir progress (accumulated time + reached section) por enrollment
- **Completion**: Reading completo cuando TODAS las secciones pasan gate → habilita comprehension test

## Relaciones

- Implementado en: [Backend Reading Gate](../backend/reading_gate.md) (services.py: process_heartbeat, check_gate)
- Relacionado: [Comprehension Test](../specs/comprehension-test.md) (test unlock post-reading)
- Relacionado: [Audit Log](../specs/audit-log.md) (log section unlock/complete events)
- Relacionado: [Course Management](../specs/course-management.md) (Section model con minTimePerSection)
- Frontend: [Components](../frontend/components.md) (PdfReader con heartbeat)

## Decisiones de diseño

- Server authority = compliance artifact (RGPD assumption 3)
- Client-only gating trivially bypassable → no trustworthy evidence
- Heartbeat tolerance configurable
- Progress persistido en ReadingProgress model (enrollment-scoped)

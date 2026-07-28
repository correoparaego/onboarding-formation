---
type: decision
title: "ADR-005. Cifrar DNI con AES-GCM y deduplicar mediante HMAC"
description: "La autorización por prefijos es fail-open para futuras rutas no clasificadas. El objetivo recomendado es denegar por defecto y declarar permisos por endpoint o namespace."
resource: TECHNICAL_DOCUMENTATION.md#L769
generated: 2026-07-28
status: active
trust_tier: human-reviewed
verified: ["9cd1545878ab4e1786ea0e301693b7275d01b015"]
---

# ADR-005. Cifrar DNI con AES-GCM y deduplicar mediante HMAC

La autorización por prefijos es fail-open para futuras rutas no clasificadas. El objetivo recomendado es denegar por defecto y declarar permisos por endpoint o namespace.

## Fuente

`TECHNICAL_DOCUMENTATION.md:769`

## Relaciones

- Parent: [5-registro-de-decisiones-de-arquitectura](./5-registro-de-decisiones-de-arquitectura.md)

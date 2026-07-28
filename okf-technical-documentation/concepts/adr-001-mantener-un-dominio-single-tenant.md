---
type: decision
title: "ADR-001. Mantener un dominio single-tenant"
description: "La autorización por prefijos es fail-open para futuras rutas no clasificadas. El objetivo recomendado es denegar por defecto y declarar permisos por endpoint o namespace."
resource: TECHNICAL_DOCUMENTATION.md#L717
generated: 2026-07-28
status: active
trust_tier: human-reviewed
verified: ["9cd1545878ab4e1786ea0e301693b7275d01b015"]
---

# ADR-001. Mantener un dominio single-tenant

La autorización por prefijos es fail-open para futuras rutas no clasificadas. El objetivo recomendado es denegar por defecto y declarar permisos por endpoint o namespace.

## Fuente

`TECHNICAL_DOCUMENTATION.md:717`

## Relaciones

- Parent: [5-registro-de-decisiones-de-arquitectura](./5-registro-de-decisiones-de-arquitectura.md)

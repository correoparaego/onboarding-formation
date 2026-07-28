---
type: documentation
title: "9.4 Enrutamiento"
description: "En el bloque /django-admin/, nginx.conf asigna X-Forwarded-Proto dos veces; la segunda asignación usa $scheme y puede contradecir el protocolo reenviado por Render. El fix del PR #32 dejó correctamente preservado /api/, pero no eliminó esta inconsistencia del Admin."
resource: TECHNICAL_DOCUMENTATION.md#L1120
generated: 2026-07-28
status: active
trust_tier: human-reviewed
verified: ["9cd1545878ab4e1786ea0e301693b7275d01b015"]
---

# 9.4 Enrutamiento

En el bloque /django-admin/, nginx.conf asigna X-Forwarded-Proto dos veces; la segunda asignación usa $scheme y puede contradecir el protocolo reenviado por Render. El fix del PR #32 dejó correctamente preservado /api/, pero no eliminó esta inconsistencia del Admin.

## Fuente

`TECHNICAL_DOCUMENTATION.md:1120`

## Relaciones

- Parent: [9-despliegue-en-render](./9-despliegue-en-render.md)
- Area: [12-anexos-de-trazabilidad](./12-anexos-de-trazabilidad.md)

---
type: documentation
title: "6.3 Cifrado y secretos"
description: "Los secretos deben inyectarse desde Render, nunca incluirse en Git o imagen. Las variables no secretas deben tener propietario, descripción y validación de arranque. La aplicación debería fallar de forma explícita en Render si falta PostgreSQL o S3, en vez de caer silenciosamente"
resource: TECHNICAL_DOCUMENTATION.md#L883
generated: 2026-07-28
status: active
trust_tier: human-reviewed
verified: ["9cd1545878ab4e1786ea0e301693b7275d01b015"]
---

# 6.3 Cifrado y secretos

Los secretos deben inyectarse desde Render, nunca incluirse en Git o imagen. Las variables no secretas deben tener propietario, descripción y validación de arranque. La aplicación debería fallar de forma explícita en Render si falta PostgreSQL o S3, en vez de caer silenciosamente

## Fuente

`TECHNICAL_DOCUMENTATION.md:883`

## Relaciones

- Parent: [6-seguridad-y-protección-de-datos](./6-seguridad-y-protección-de-datos.md)
- Area: [12-anexos-de-trazabilidad](./12-anexos-de-trazabilidad.md)

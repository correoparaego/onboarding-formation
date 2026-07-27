---
type: frontend-module
resource: frontend/src/components/
tags: [react, components, ui, layout, pdf-reader, error-boundary]
description: Shared components - UI primitives, layout, PDF reader, error boundary
status: active
generated: 2026-07-27
---

# Components (Frontend)

Componentes compartidos — primitivas UI, layout, lector PDF, error boundary.

## UI Primitives (13 componentes)

- Button, Card, Badge, Input, Modal, EmptyState, Spinner, Skeleton, Toast, ConfirmDialog, ProgressBar, ThemeToggle, ResponsiveTable

## Layout

- **AdminLayout.tsx**: Sidebar + responsive layout
- **AdminSidebar.tsx**: Navegación lateral
- **Breadcrumb.tsx**: Breadcrumb navigation
- **NetworkBanner.tsx**: Online/offline banner

## Components

- **PdfReader/index.tsx**: Lector PDF con heartbeat (active-time tracking)
- **ErrorBoundary.tsx**: Error boundary wrapper

## Relaciones

- Spec: [Timed Reading](../specs/timed-reading.md) (PdfReader heartbeat)
- Usado por: [Admin](../frontend/admin.md) (layout, UI)
- Usado por: [Employee](../frontend/employee.md) (PdfReader, UI)
- Usado por: [Auth](../frontend/auth.md) (UI primitives)

## Patrones clave

- Barrel export via ui/index.ts
- PdfReader envía heartbeats al backend (active-time validation)
- ThemeToggle integrado en AdminSidebar
- ResponsiveTable para tablas adaptables

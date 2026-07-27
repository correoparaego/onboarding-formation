---
type: backend-module
resource: backend/ai_generation/
tags: [django, app, ai, llm, openai, generation, encryption, pii, hitl]
description: AI content generation with BYO LLM key, OpenAI-compatible client, PII protection
status: active
generated: 2026-07-27
---

# AI Generation (Django App)

App Django para generación de contenido con LLM externo, BYO key, y protección PII.

## Modelos

- **AdminLLMKey**: API key cifrada por admin (AES-GCM, nunca expuesta)

## Views/APIs

- Admin: store LLM key (POST /api/ai/key)
- Admin: guided content generation (POST /api/ai/generate-content)
- Admin: PDF-to-test generation (POST /api/ai/generate-test)

## Client

- **OpenAICompatibleClient**: Interfaz unificada (base_url, api_key, model) para cualquier provider
- **FakeLLMClient**: Mock para testing (no API calls)

## Relaciones

- Spec: [AI Generation](../specs/ai-generation.md)
- Relacionado: [Course Management](../specs/course-management.md) (content/test generation)
- Frontend: [Admin](../frontend/admin.md) (AiKeyForm, GuidedContent, PdfTestGen - lazy loaded)

## Dependencias

- Importa: [Common](../backend/common.md) (crypto para key encryption)
- No tiene circular dependencies
- Sanitizer deliberadamente NO importa employees (PII exclusion by construction)

## Patrones clave

- Provider-agnostic: OpenAI-compatible interface
- AdminLLMKey cifrado con AES-GCM + random nonce
- Raw key NUNCA en serialized responses
- Sanitizer: PII exclusion by construction (no importa employees)
- HITL: draft NO se persiste hasta explicit save del admin

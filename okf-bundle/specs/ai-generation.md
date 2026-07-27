---
type: spec
resource: openspec/specs/ai-generation/spec.md
tags: [ai, llm, openai, generation, hitl, encryption, pii]
description: AI content generation with BYO LLM key, HITL workflow, and PII protection
status: active
generated: 2026-07-27
---

# AI Generation

Generación de contenido y tests con LLM externo (BYO key), human-in-the-loop, y protección PII.

## Requisitos clave

- **BYO LLM Key**: Admin almacena su propia API key (OpenAI-compatible), cifrada at-rest
- **Key Isolation**: Raw key NUNCA se expone en respuestas, logs, audit, o rutas employee
- **OpenAI-Compatible Client**: Interfaz unificada (base_url, api_key, model) para cualquier provider
- **Guided Content Gen**: Admin responde preguntas guiadas + sube docs → draft para revisión
- **PDF-to-Test Gen**: Admin sube PDF → AI genera questions para question bank
- **HITL**: Draft NO se persiste hasta explicit save del admin
- **PII Guard**: Sanitizer excluye PII antes de enviar a LLM (sanitizer NO importa employees)

## Relaciones

- Implementado en: [Backend AI Generation](../backend/ai_generation.md)
- Relacionado: [Course Management](../specs/course-management.md) (content/test generation)
- Relacionado: [Common](../backend/common.md) (crypto para key encryption)
- Frontend: [Admin](../frontend/admin.md) (AiKeyForm, GuidedContent, PdfTestGen - lazy loaded)

## Decisiones de diseño

- Provider-agnostic: OpenAI-compatible interface (OpenAI/Groq/Together/Ollama)
- FakeLLMClient para testing (no API calls)
- Sanitizer deliberadamente NO importa employees (PII exclusion by construction)
- AdminLLMKey cifrado con AES-GCM + random nonce
- Raw key NUNCA en serialized responses (override de to_representation)

# Delta for ai-generation

## ADDED Requirements

### Requirement: BYO LLM Key Storage

The system MUST allow an admin to store their own LLM API key. The key MUST be stored encrypted at rest and scoped per admin. The raw key MUST NOT be sent to the client/employee and MUST NOT be written to logs, audit, or error traces.
(WHY: admin owns the key/billing and secret management; RGPD Art.32 — security of processing.)

#### Scenario: Key stored encrypted and never exposed

- GIVEN an authenticated admin
- WHEN the admin submits an LLM API key via POST /api/ai/key
- THEN the key is stored encrypted at rest and associated with that admin only
- AND no API response, client payload, or log/audit entry contains the raw key

#### Scenario: Employee routes never load the key

- GIVEN an employee request to any employee route
- WHEN the route is served
- THEN the raw LLM key is absent from the response and is not loaded server-side

### Requirement: OpenAI-Compatible Client

The system SHALL invoke the LLM through a single OpenAI-compatible interface parameterized by (base_url, api_key, model), so any compatible provider works without per-provider branching.
(WHY: provider-agnostic abstraction — one code path covers OpenAI/Groq/Together/Ollama-local.)

#### Scenario: Generation uses stored provider config

- GIVEN an admin has stored base_url, api_key, and model
- WHEN a generation request is made
- THEN the call routes through the OpenAI-compatible client with those parameters
- AND no provider-specific code branch is required

### Requirement: Guided Content Generation

The system SHALL generate a draft course content from the admin's structured answers to guided questions plus uploaded reference documents, using the admin's key. The draft SHALL be returned for review/edit and MUST NOT be persisted until the admin explicitly saves it.
(WHY: human-in-the-loop quality and compliance.)

#### Scenario: Draft returned then saved on explicit admin save

- GIVEN an admin submits Q&A plus reference documents
- WHEN the generation completes
- THEN a draft Course/Sections payload is returned for review
- AND on explicit admin save the Course and Sections are created

#### Scenario: No silent persistence

- GIVEN a generation completes
- WHEN the admin does not send an explicit save
- THEN no Course or Section row is written

### Requirement: PDF-to-Test Generation

The system SHALL extract text from an uploaded PDF and generate a comprehension test (exactly one correct answer per question) using the admin's key. The draft QuestionBank SHALL be reviewed/edited and MUST NOT be persisted until the admin explicitly saves it.

#### Scenario: PDF yields editable single-correct question bank

- GIVEN an admin uploads a PDF
- WHEN text is extracted and the LLM returns questions
- THEN a draft QuestionBank with single-correct answers is returned
- AND after admin edit and explicit save it is persisted

### Requirement: PII Exclusion Guard

Prompts sent to the LLM MUST be built ONLY from course content, reference documents, and extracted PDF text. Employee PII (DNI, name, email, phone) MUST NOT be included in any LLM call.
(WHY: RGPD Art.5/Art.6 — no disclosure of personal data to an external processor; enforced by construction.)

#### Scenario: Employee data excluded from prompt

- GIVEN a generation request that includes employee records
- WHEN the prompt is assembled
- THEN all DNI/name/email/phone values are stripped so the built prompt contains no employee PII

### Requirement: Human-in-the-Loop Persistence

Generated content and tests are drafts. The system MUST NOT persist them until the admin explicitly confirms. Single-correct-answer validation applies to generated tests.
(WHY: quality gate + compliance; generated artifacts require human review.)

#### Scenario: Multiple-correct test rejected at save

- GIVEN a generated test draft with more than one marked-correct option
- WHEN the admin attempts to save
- THEN the save is rejected until exactly one correct answer remains

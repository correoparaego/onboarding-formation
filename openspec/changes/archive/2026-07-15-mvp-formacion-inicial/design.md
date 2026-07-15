# Design: MVP Formación Inicial

## Technical Approach
Two independent deploy units: Django (Python) JSON API on an EU PaaS, and a React/Vite SPA on a static EU host. PostgreSQL via Django ORM. The server-authoritative reading-time gate plus the append-only `AuditEvent` form the compliance core. Django serves `/admin` + API routes; React is static-hosted and consumes the JSON API over CORS using an env-configured base URL.

## Architecture Decisions
| Decision | Options | Choice | Rationale |
|---|---|---|---|
| Tenancy | multi-tenant vs single-tenant | **Single-tenant** | MVP = one company (idea §7); isolation adds cost now; phase-2 adds tenancy |
| Reading gate | client-only vs server-authoritative | **Server-authoritative** | Client gating is bypassable; server accumulation is the evidence (RGPD 3) |
| Test subset | random vs deterministic seeded | **Deterministic per attempt** | Reproducible, distinct, auditable subsets |
| Cert PDF | reportlab vs WeasyPrint | **reportlab primary, WeasyPrint fallback** | reportlab simpler for dynamic fields; both printable |
| Email transport | Resend vs SMTP | **Configurable both** | Switch without code change (notifications spec) |
| Auth | password both vs magic-link employee | **Admin session + employee magic-link/code** | Weak binding accepted (RGPD 4) |
| AI key | platform-managed key vs BYO per-admin | **BYO LLM key + OpenAI-compatible client** | Admin owns key/billing; one abstraction covers providers (OpenAI/Groq/Together/Ollama); key never reaches client/employee |

## Tenancy Model (explicit, config rule)
**SINGLE-TENANT** for MVP. No `company`/`tenant_id` partitioning. **Rationale:** idea.txt §7 scopes MVP to a single company; multi-tenant strict isolation (idea §6 risk) is deferred to phase-2. **Note:** models stay tenant-agnostic (no global `tenant_id` column) so phase-2 can introduce a tenant boundary (shared schema with `tenant_id`, or schema-per-tenant) without model rewrites.

## Architecture Overview
**Django apps:** `courses` (Course, Section, QuestionBank, Question), `employees` (Employee + Excel import), `reading_gate` (Enrollment, ReadingProgress, gate API, AuditEvent, expediente), `certificates` (Badge, EmployeeBadge, PDF gen), `notifications` (email send), `authentication` (admin session, employee token), `ai_generation` (encrypted per-admin key store, OpenAI-compatible client wrapper, guided-content + PDF→test generation endpoints, review payload contract, PII-exclusion guard).
**Frontend (React/Vite):** `src/admin/*` (import, course CRUD, catalog, expediente), `src/admin/ai/*` (key entry form, guided Q&A, review/edit UI for generated content & tests), `src/employee/*` (token reader, test, badges), `src/components/PdfReader` (pdfjs-dist, section-gated), `src/api/*` (fetch client), `src/i18n` (react-i18next, es default).

## AI Generation Design

AI authoring is **in scope** for MVP via bring-your-own (BYO) key. The platform never owns an LLM key; each admin supplies their own and bears provider billing. Two generation modes: (A) guided course content from admin answers + reference docs, (B) PDF→test generation. Both are **human-in-the-loop**: the backend returns a draft; persistence happens only after explicit admin save.

### Key Storage (security requirement)
An encrypted credential store keyed to the Admin user (`AdminLLMKey`, see Data Model). The raw key is read **server-side only** when the admin triggers a generation. It is:
- **NEVER** serialized to the client (no admin/employee API response includes the raw key);
- **NEVER** written to logs, audit, or error traces;
- **NEVER** available on any employee route (admin-only enforcement).
Implementation: encrypted `CharField` (app-level envelope encryption or DB encryption-at-rest) — the key at rest is opaque to DB operators.

### Client
A thin **OpenAI-compatible wrapper** taking `(base_url, api_key, model)` from the admin's stored config. Provider-agnostic: one abstraction covers OpenAI, Groq, Together, and Ollama (local) without code branching per provider. All provider calls go through this single interface so it is fully mockable in tests.

### Guided Content Flow (mode A)
```
Admin answers structured Q&A + uploads reference docs ─▶ ai_generation backend
   backend builds prompt from COURSE-ONLY material ─▶ LLM (admin's key, server-side)
   ◀── draft sections/content ──────────────────────────┘
Admin reviews/edits in src/admin/ai UI ─▶ on save: creates Course + Sections (+ optional PDF render)
```

### PDF→Test Flow (mode B)
```
Admin uploads PDF ─▶ server extracts text (pdfplumber / PyPDF2)
   backend builds prompt from EXTRACTED TEXT ─▶ LLM (admin's key)
   ◀── QuestionBank draft (single-correct enforced) ─┘
Admin reviews/edits in src/admin/ai UI ─▶ on save: persists to QuestionBank
```

### PII Guard (HARD design constraint)
LLM prompts are assembled **only** from: course content, admin reference docs, and extracted PDF text. Employee PII (DNI, name, email, phone) is structurally excluded — the prompt builder never concatenates any employee record into the request. This is enforced by construction (the sanitization boundary has no access to the Employee queryset), not by optional flag.

### Human-in-the-Loop
Generated artifacts are **drafts**. The backend returns a review payload; nothing is written to `Course`/`Section`/`QuestionBank` until the admin sends an explicit save call. Generation failures return an error payload, never a partial silent write.

## Data Model (Django ORM)
- **Employee**: `dni` CharField (verbatim, unique, no normalization), name, position, email, phone.
- **Course**: title, pdf_file, position_catalog (M2M Position→Course), `min_time_divisor` (default 3).
- **Section**: FK Course, `order`, `section_base` (seconds).
- **QuestionBank**: FK Course. **Question**: FK Bank, text, options JSON, `correct_index` (single, validated).
- **Enrollment**: FK Employee + Course, `status` (assigned/in_progress/complete/passed/failed_exhausted), `attempts_used`.
- **ReadingProgress**: FK Enrollment + Section, `accumulated_time`, `reached_section`, `device_id`, `session_id` (unique per enrollment).
- **AuditEvent**: append-only; `enrollment`, `event_type`, `device_id`, `session_id`, `timestamp`, `payload` JSON. No update/delete API.
- **Badge** (slug, label), **EmployeeBadge** (FK Employee+Badge, unique).
- **AdminLLMKey** (LLM credential): FK Admin user (one-to-one/one-per-admin), `encrypted_key` (encrypted CharField — raw key never stored in plaintext), `provider` (label), `base_url`, `model`, `status` (active/inactive). Raw key is NOT written to audit/logs; `encrypted_key` is read server-side only during a generation call.

## Reading-Gate Sequence
```
Client (PdfReader) ──heartbeat(t,visibility,interaction)──▶ reading_gate API
        ◀── accumulated / remaining / locked ──────────────┘
API validates visibility+interaction; credits delta to Postgres ReadingProgress
When accumulated >= minTimePerSection (= section_base/3): unlock next
All sections done → status=complete → test unlocks
Cross-device: ReadingProgress keyed by enrollment restored on new device
```

## Comprehension-Test Flow
On reading complete: ≤3 attempts. Each attempt draws a distinct subset via `seed = hash(enrollment_id, attempt_no)` deterministic shuffle of the bank. Fail (`score < pass`) resets ReadingProgress to section 1 / 0s and increments `attempts_used`. 4th attempt blocked → `failed_exhausted`. Pass → `status=passed`, cert available, badges evaluated. Single correct answer enforced at authoring.

## Auth
Admin: username/password → Django session; logout invalidates. Employee: magic-link/code (single-use, TTL) issued per enrollment; consumption invalidates token; session scoped to that employee only; employee routes isolated from admin (403). Raw token never in audit/log plaintext. AI endpoints (`/api/ai/*`) are admin-only; the raw LLM key is never present on any employee route and is never serialized to the client.

## Certificate Generation
`certificates` builds PDF (reportlab) from Course doc + Employee (name + DNI verbatim) + evaluation + summary index. No e-signature (RGPD 2). One active cert per passed enrollment; regeneration reproduces identical core fields.

## Notifications
Django `send_mail` via configured backend (Resend API or SMTP). Spanish templates (access, reminder, completion). Log attempts (recipient + status) without raw token/secrets.

## Audit & Compliance Notes
`AuditEvent` is the compliance artifact (append-only). **Accepted constraints:** (RGPD 3) server gating = "reasonable control" — cannot prove human presence; (RGPD 4) email possession ≈ identity = weak binding. Documented, not mitigated at MVP (phase-2: code+DNI/2FA, WORM if mandated).

## API Contract Sketch
| Endpoint | Purpose |
|---|---|
| `POST /api/import` | Excel parse/validate, dedupe by DNI, report |
| `POST/GET /api/courses` | CRUD, sections, bank |
| `POST /api/enroll` | assign mandatory courses by position |
| `POST /api/reading/heartbeat` | validate + accumulate, return unlock state |
| `POST /api/test/submit` | grade attempt, distinct subset logic |
| `GET /api/certificate/{enrollment}` | PDF |
| `GET /api/expediente?course=&status=` | filters |
| internal `AuditEvent` append | reading/exam/cert events |
| `POST /api/ai/key` | admin-only: set/update encrypted LLM key (provider/base_url/model) |
| `POST /api/ai/generate-content` | admin-only: guided content draft from Q&A + reference docs |
| `POST /api/ai/generate-tests` | admin-only: PDF→QuestionBank draft (PDF upload); single-correct enforced |

## Testing Strategy
| Layer | Test | Approach |
|---|---|---|
| Unit | gate math, subset determinism, DNI verbatim | pytest |
| Integration | heartbeat→unlock, fail→restart, cert gen | APIClient + Postgres |
| E2E | import→read→test→cert | Playwright on SPA |
| Unit | LLM client mock + PII-exclusion sanitizer | LLM client behind an interface with a fake implementation — unit/integration tests NEVER call a real provider; assert the sanitizer rejects/excludes any employee PII from the built prompt |
| Integration | generate-content/generate-tests with fake LLM | APIClient + fake provider returns draft; assert no raw key in response/logs; assert persistence only on explicit save |

## Threat Matrix
N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary in this design.

## Migration / Rollout
Fresh `migrate`; seed 3 badges; no destructive data. Idempotent imports by DNI+course. Audit/certs retained across rollback.

## Open Questions
None blocking. The concrete LLM provider list is the admin's choice (any OpenAI-compatible endpoint); the abstraction supports OpenAI, Groq, Together, and Ollama-local without code change.

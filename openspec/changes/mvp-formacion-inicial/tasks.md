# Tasks: MVP Formación Inicial

> Stack: Django (Python) + React/Vite SPA + PostgreSQL. Single-tenant MVP. Threat matrix N/A (no RED-test tasks required).

## Phase 1: Project Scaffolding
- [x] 1.1 Init Django project + `courses, employees, reading_gate, certificates, notifications, authentication` apps; PostgreSQL settings. [design §Architecture Overview]
- [x] 1.2 Scaffold React/Vite SPA (`src/admin/*`, `src/employee/*`, `src/components/PdfReader`, `src/api/*`, `src/i18n`). [design §Architecture Overview]
- [x] 1.3 Configure CORS (env base URL), DRF JSON API, `react-i18next` Spanish default. [proposal §Library map]
- [x] 1.4 Encrypt-at-rest DNI config + retention settings hook. [proposal §RGPD 1]

## Phase 2: Data Model & Migrations
- [x] 2.1 `employees.Employee`: dni (verbatim, unique), name, position, email, phone. [spec employee-import; design §Data Model]
- [x] 2.2 `courses.Course/Section/QuestionBank/Question` (+ `min_time_divisor`, `section_base`, single-correct validation). [spec course-management]
- [x] 2.3 `reading_gate.Enrollment/ReadingProgress/AuditEvent` (+ `expediente` fields). [design §Data Model; spec audit-log]
- [x] 2.4 `certificates.Badge/EmployeeBadge`. [spec badges]
- [x] 2.5 Generate + review migrations (`makemigrations`/`migrate`). [proposal §Rollback Plan]

## Phase 3: Authentication
- [x] 3.1 Admin username/password session login/logout (Django session). [spec authentication]
- [x] 3.2 Employee single-use magic-link/code token (TTL, consumed invalidated; raw token never in logs). [spec authentication; secure-access]
- [x] 3.3 Middleware enforcing admin↔employee route isolation (403). [spec authentication §Session Isolation]

## Phase 4: Employee Import
- [x] 4.1 `POST /api/import` Excel parse via openpyxl/pandas → Employee rows. [spec employee-import §Parsing]
- [x] 4.2 DNI stored verbatim (no trim/normalize); validation report (missing field, bad email, bad DNI). [spec employee-import §Verbatim/§Report]
- [x] 4.3 Dedupe by DNI; reject/flag duplicates. [spec employee-import §Dedupe]
- [x] 4.4 Import idempotent; auto-enrollment deferred to Phase 7 (per scope decision — only Employee records + report created here). [spec enrollment-assignment]

## Phase 5: Course Management
- [x] 5.1 Admin course CRUD + PDF upload + ordered sections. [spec course-management §PDF Authoring]
- [x] 5.2 Question bank authoring (single-correct enforced on save). [spec course-management §Bank; comprehension-test §Single Correct]
- [x] 5.3 Position→catalog M2M mapping + lookup endpoint. [spec course-management §Catalog]

## Phase 6: AI Generation
- [x] 6.1 `ai_generation.AdminLLMKey` model (FK Admin, `encrypted_key`, provider, base_url, model, status) + `makemigrations ai_generation`. [spec ai-generation §BYO; design §Key Storage]
- [x] 6.2 `POST /api/ai/key` admin-only: set/update encrypted key; raw key never in response/logs. [design API; spec ai-generation §BYO]
- [x] 6.3 OpenAI-compatible client wrapper `(base_url, api_key, model)` behind interface + fake/mock impl for tests. [design §Client; design §Testing]
- [x] 6.4 PII-exclusion sanitizer (course/PDF content only; never Employee queryset) + unit test asserting DNI/name/email/phone stripped. [spec ai-generation §PII; design §PII Guard]
- [x] 6.5 `POST /api/ai/generate-content`: guided Q&A + reference docs → Course/Sections draft returned for review, not persisted. [spec ai-generation §Guided; design §Guided Flow]
- [x] 6.6 `POST /api/ai/generate-tests`: PDF→QuestionBank draft (server text extraction → LLM, single-correct) returned for review, not persisted. [spec ai-generation §PDF; design §PDF Flow]
- [x] 6.7 Frontend `src/admin/ai/*`: key entry form, guided Q&A UI, review/edit UI for generated content & tests, save to Course/QuestionBank. [design §Architecture Overview; design frontend]
- [x] 6.8 Human-in-the-loop persistence guard: drafts not saved until admin confirms; single-correct enforced; multi-correct draft rejected at save. [spec ai-generation §HITL]

## Phase 7: Enrollment Assignment
- [x] 7.1 Auto-create enrollment(s) per position's mandatory courses on import (status=assigned). [spec enrollment-assignment §Mandatory]
- [x] 7.2 Idempotency by DNI+course (re-import skips duplicates). [spec enrollment-assignment §Idempotency]

## Phase 8: Secure Access & Notifications
- [ ] 8.1 Token issuance per pending enrollment (single-use, TTL) on assignment. [spec secure-access §Issuance]
- [ ] 8.2 Token consumption invalidation + reuse block. [spec secure-access §Consumption]
- [ ] 8.3 Configurable email transport (Resend/SMTP) + Spanish templates (access/reminder/completion). [spec notifications]
- [ ] 8.4 Delivery logging (recipient/status, no raw token/secrets). [spec notifications §Logging]

## Phase 9: Timed Reading Gate
- [x] 9.1 `POST /api/reading/heartbeat`: validate visibility+interaction, credit delta. [spec timed-reading §Heartbeat; design §Sequence]
- [x] 9.2 Server gate: unlock only when accumulated ≥ `section_base/3`. [spec timed-reading §Server-Gated]
- [x] 9.3 `ReadingProgress` per enrollment; cross-device resume. [spec timed-reading §Cross-Device]
- [x] 9.4 All sections passed → status=complete, test unlocks. [spec timed-reading §Completion]

## Phase 10: Comprehension Test
- [x] 10.1 `POST /api/test/submit`: grade attempt; ≤3 attempts; 4th blocked→failed_exhausted. [spec comprehension-test §Max Three]
- [x] 10.2 Deterministic distinct subset per attempt (`seed=hash(enrollment,attempt)`). [spec comprehension-test §Distinct; design §Test Flow]
- [x] 10.3 Fail resets ReadingProgress to section 1/0s, increments attempts_used. [spec comprehension-test §Fail Restart]
- [x] 10.4 Pass → status=passed; enable cert + badge evaluation. [spec comprehension-test §Pass]

## Phase 11: Certificate
- [ ] 11.1 `GET /api/certificate/{enrollment}`: reportlab PDF (name, DNI verbatim, date, title, evaluation, summary index). [spec certificate]
- [ ] 11.2 One active cert per passed enrollment; idempotent regeneration. [spec certificate §One Per]

## Phase 12: Badges
- [ ] 12.1 Seed initial badges ("Primer curso", "Catálogo completo", "Sin fallos"). [spec badges §Initial Set]
- [ ] 12.2 Award logic on pass: first, all-position, clean-first-attempt. [spec badges §Award*]

## Phase 13: Expediente & Filters
- [ ] 13.1 Persist per-enrollment result (status, attempts, score, dates). [spec expediente §Storage]
- [ ] 13.2 Admin filter `GET /api/expediente?course=&status=`. [spec expediente §Filter]
- [ ] 13.3 Retention policy; records survive rollback. [spec expediente §Retention]

## Phase 14: Audit Log
- [ ] 14.1 `AuditEvent` append-only model + API; reject update/delete. [spec audit-log §Append/§No Mutation]
- [ ] 14.2 Capture device/session/enrollment/timestamp context. [spec audit-log §Context]
- [ ] 14.3 Wire coverage: section unlock/complete, attempt start/submit/result, cert issuance. [spec audit-log §Coverage]

## Phase 15: Verification / QA
- [ ] 15.1 Unit: gate math, subset determinism, DNI verbatim, sanitizer (pytest). [design §Testing]
- [ ] 15.2 Integration: heartbeat→unlock, fail→restart, cert gen, AI fake-LLM flows (APIClient+Postgres). [design §Testing]
- [ ] 15.3 E2E Playwright: import→read→test→cert on SPA. [design §Testing]
- [ ] 15.4 README/run docs + deployment env notes (EU PaaS). [proposal §Dependencies]

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~2200–3600+ (greenfield, 14 areas, 2 deploy units) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1 Scaffold+Models → PR2 Auth+Import → PR3 Courses+Enroll+AI → PR4 Reading+Test → PR5 Cert+Badges+Expediente → PR6 Audit+QA |
| Delivery strategy | auto-forecast (auto-chain on high) |
| Chain strategy | pending (recommend stacked-to-main) |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units (PR slices)
| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Scaffold + models/migrations | PR1 | `pytest employees courses` | `manage.py migrate` + `/admin` boot | Drop app migrations / revert scaffold |
| 2 | Auth + employee import | PR2 | `pytest authentication employees` | Admin login + import dry-run | Auth views + import endpoint |
| 3 | Course mgmt + enrollment + AI generation | PR3 | `pytest courses enrollment ai_generation` | Catalog + auto-enroll + AI key/guided/PDF flows | Courses/enrollment/ai models |
| 4 | Timed gate + test | PR4 | `pytest reading_gate comprehension` | Heartbeat→unlock→fail→restart | Reading_gate tables |
| 5 | Cert + badges + expediente | PR5 | `pytest certificates badges expediente` | Pass→PDF→badge→filter | Cert/badge/expediente |
| 6 | Audit + QA/E2E | PR6 | `pytest --cov ; playwright` | Append-only + full E2E | Audit model (immutable retained) |

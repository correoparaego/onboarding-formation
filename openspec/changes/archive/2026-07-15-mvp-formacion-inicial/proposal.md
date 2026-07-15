# Proposal: MVP Formación Inicial

## Intent
Build a single-company internal web app for mandatory employee onboarding/training: Excel employee import, admin-authored PDF courses with a server-gated timed reader, comprehension tests, printable certificates, minimal badges, and cross-device audit logs. Replaces manual/oral training that leaves no compliance evidence trail.

## Scope
### In Scope
- Admin: Excel import, course CRUD (PDF + authored test/bank), position→catalog, expedientes, cert generation
- Admin AI-assisted authoring: BYO LLM API key → guided course content generation + PDF→test generation (human-in-the-loop review before save)
- Employee: token-gated timed PDF reader, comprehension test (≤3 attempts), initial badges
- Server-authoritative reading-time gate + append-only audit (cross-device resume)
- Email-only notifications; Spanish UI; i18n scaffold

### Out of Scope (MVP)
- Multi-tenant / platform super-admin
- SMS/WhatsApp channels
- Full gamification (levels/leaderboards/points economy)
- E-signature / qualified cert validity
- Individual employee CRUD UI (Excel-only import)
- (Phase-2: fully autonomous course generation from scratch — admin provides only topic + reference docs, agent produces full course.)

## Capabilities (contract with sdd-spec)
### New Capabilities
- `employee-import`: Excel parse/validate (DNI verbatim), dedup
- `course-management`: PDF + test/bank authoring, catalog by position
- `enrollment-assignment`: mandatory course assignment per position
- `secure-access`: email token/link issuance + delivery
- `timed-reading`: server-gated viewer, time-gate, cross-device resume
- `comprehension-test`: ≤3 attempts, distinct subsets, fail→restart
- `certificate`: printable PDF (employee data, date, title, evaluation, summary index)
- `badges`: initial badge set + award logic
- `expediente`: result storage + admin filters
- `audit-log`: append-only reading/exam events
- `notifications`: email (Resend/SMTP, configurable)
- `authentication`: admin password session + employee magic-link/code
- `ai-generation`: admin BYO LLM API key; mode A guided course content generation (from admin answers + reference docs); mode B PDF→test generation from uploaded PDF; human-in-the-loop review before persistence; PII-exclusion guard (no employee DNI/name/email/phone sent to LLM)
### Modified Capabilities
- None (greenfield)

## Approach
**STACK CONFIRMED (Django + React/Vite):** Team uses Python → locked to Option B from exploration. Django (Python) full backend + React (Vite) SPA frontend + PostgreSQL (Django ORM).

Server-authoritative reading-time gate + cross-device audit. The PDF.js viewer is a client React component that reports activity heartbeats; Django API endpoints accumulate validated active time in Postgres and grant section unlock only after `minTimePerSection = sectionBase/3` (configurable per course).

AI generation uses an OpenAI-compatible client configured per admin with their own key (server-stored, encrypted at rest, never exposed to client/employee and never logged). Generation calls send ONLY course content, reference documents, or extracted PDF text — never employee PII (DNI, name, email, phone). Generated content and tests are presented to the admin for review/edit BEFORE being saved to the course / QuestionBank; generated tests still enforce a single correct answer.

### Library / component map
- **Backend (Django):** Django + DRF (or Django API/views) exposing JSON APIs; Employee import via `openpyxl`/`pandas`; certificate PDF via `reportlab` (or `WeasyPrint`); email via Django `send_mail`/SMTP (Resend/SMTP); auth via `django-allauth`/session — admin password session + employee magic-link/code.
- **Frontend (React + Vite SPA):** `pdfjs-dist`/`react-pdf` page/section-gated client component; `react-hook-form` + `zod` validation; `react-i18next` (Spanish default); consumes the Django JSON API.
- **Reading-time gate + audit:** Django API endpoints + Postgres tables; server-authoritative, cross-device resume keyed by enrollment (the compliance artifact).

## RGPD/LOPDGDD Assumptions (PRODUCT OWNER MUST CONFIRM)
1. **DNI storage verbatim** — lawful basis + privacy notice (Art.13/14) provided by company; encryption at rest + retention policy applied.
2. **Certificate legal validity** — printable PDF, NO e-signature; internal record only; formal validity not required at MVP.
3. **Reading-time integrity** — server gating + heartbeats + visibility checks + immutable audit accepted as "reasonable control," not human-presence proof.
4. **Identity binding** — email possession ≈ identity for MVP; weak binding accepted.
5. **AI generation (BYO key)** — admin-provided key + course-only data; platform stores the key encrypted server-side, never logs it, never exposes it to employees; employee PII (DNI/name/email/phone) is excluded from all LLM calls. Admin bears their own LLM provider cost; generated artifacts require human-in-the-loop review before persistence.

## Open Questions → MVP Defaults
| Q | Default | Blocker? |
|---|---------|----------|
| Q1 team familiarity | Python → Django (backend) + React/Vite (frontend) | Resolved — Django+React |
| Q2 hosting/residency | EU-region managed PaaS: Python host for Django (Render/Railway/Fly.io EU) + static EU host for React build | Resolved — EU PaaS |
| Q3 auth | employee magic-link/code; admin password session | No |
| Q4 employee creation | Excel-only import | No |
| Q5 reading formula | baseline=estChars÷comfortSpeed; minTime=base/3; server-authoritative; per-course config | No |
| Q6 fail/restart | each fail restarts reading; ≤3 attempts; distinct subset each | No |
| Q7 cert fields | per idea.txt; retention=emp-end+legal period (assumption) | No |
| Q8 audit tamper | append-only log; WORM only if mandated (flag) | No |
| Q9 badges | "Primer curso", "Catálogo completo", "Sin fallos" | No |
| Q10 email | Resend/SMTP (configurable) | No |
| Q11 AI provider abstraction | OpenAI-compatible client (base_url + api_key + model) — covers OpenAI/Groq/Together/Ollama-local via one abstraction | No (non-blocker) |

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| `backend/<apps>/models.py` + Django ORM migrations | New | Employee, Course, Section, Test/QuestionBank, Enrollment, Progress, Audit, Badge (replaces Prisma schema) |
| `backend/courses/` (Django app) | New | course/section/test/bank authoring, catalog by position, admin CRUD |
| `backend/employees/` (Django app) | New | Employee model + Excel import parse/validate (`openpyxl`/`pandas`), expediente storage |
| `backend/reading_gate/` (Django app) | New | authoritative time gate API + append-only audit (critical) |
| `backend/certificates/` (Django app) | New | cert PDF gen (`reportlab`/`WeasyPrint`), badge award logic |
| `backend/notifications/` (Django app) | New | email send (Django `send_mail`/SMTP) |
| `backend/authentication/` (Django app) | New | admin password session + employee magic-link/code |
| `backend/ai_generation/` (Django app) | New | encrypted per-admin API key storage, OpenAI-compatible generation client, guided content + PDF→test endpoints, human-in-the-loop review flow, PII-exclusion guard |
| `frontend/src/` (React + Vite SPA) | New | admin screens, employee token reader, test, badge views, PDF viewer, forms |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Reading-time not absolute | Med | server gating + audit; document limitation |
| Weak identity binding | Med | flag; phase-2 code+DNI/2FA |
| RGPD DNI exposure | High | encryption at rest, retention, privacy notice |
| Stack/deploy mismatch | Low | stack locked to Django+React; EU PaaS hosting chosen |
| Excel edge cases block onboarding | Med | strict server-side validation + report |
| API-key secret management | Med | encrypt at rest, per-admin, never logged/exposed to client |
| Third-party data exposure | Med | PII-exclusion guard; only course/PDF content sent to LLM |
| Generated-content quality | Low | human-in-the-loop review before persistence |
| Admin's own LLM cost | Low/info | admin owns provider billing; surfaced in UI |

## Rollback Plan
- **DB:** restore pre-migration snapshot; all schema changes versioned via Django `migrate` / `migrate <app> zero` rollback.
- **App:** redeploy previous tagged release; no DB-destructive seed required for features.
- **Data:** employee/course imports idempotent by DNI/course id; re-import corrects.
- **Audit/certs:** immutable logs retained for compliance; rollback does not purge.
- **Verify:** post-rollback smoke test (import → read → cert) on staging.

## Dependencies
- PostgreSQL instance (EU region, managed)
- Python-friendly EU managed PaaS for the Django backend (e.g. Render / Railway / Fly.io EU)
- Static EU hosting for the React (Vite) build
- Resend/SMTP account for email

## Success Criteria
- [ ] Excel import creates employees with DNI verbatim + validation report
- [ ] Timed reader blocks advance until server-confirmed minTime; resumes cross-device
- [ ] Test ≤3 attempts, distinct subsets, fail restarts reading
- [ ] Cert PDF generated with required fields; badges awarded
- [ ] Admin expediente filters return correct completions
- [ ] Append-only audit log records reading/exam events
- [ ] Admin can enter BYO LLM key; guided content + PDF→test generation work with human-in-the-loop review; no employee PII sent to LLM

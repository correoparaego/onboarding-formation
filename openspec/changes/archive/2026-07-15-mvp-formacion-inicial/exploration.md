# Exploration: mvp-formacion-inicial

> Phase: `sdd-explore` (openspec backend). Change: `mvp-formacion-inicial`.
> Project: onboarding-formation. Mode: greenfield — no code, no manifest, no stack detected.
> Language note: technical artifact in English per SDD contract; product/UI content stays Spanish.

## 1. Current State

- **Greenfield.** No `package.json`/`go.mod`/`pyproject.toml`/`Cargo.toml`, no source, no test runner, no linter/formatter. `openspec/config.yaml` confirms stack NOT detected.
- **Product brief** (`idea.txt`, Spanish) + confirmed decisions from the user define an internal, single-company employee onboarding/training web app.
- **Confirmed MVP constraints (do NOT reopen):** single company (no multi-tenant); Excel employee import; timed PDF reader + manual comprehension test; email-only notifications; basic printable PDF certificate; minimal gamification (initial badges); i18n scaffold but Spanish-only now; audit logs across devices; time control = block advancing faster than 3× average reading speed; DNI stored verbatim (no verification, no special encryption); no payment gateway; AI course generation deferred.

## 2. MVP Scope (tightened)

### Actors (MVP)
- **Admin (single company):** imports employees, creates/edits courses (PDF + authored test + question bank), assigns catalog by position, consults expedientes, generates certificates.
- **Employee:** receives secure access, reads timed PDF, takes test, earns initial badges.
- *(No platform super-admin / multi-tenant in MVP.)*

### Core flows
1. Admin imports employees via Excel (DNI stored exactly as provided).
2. Admin creates a course: upload PDF, author test with a question bank, link to position(s) in catalog.
3. System assigns mandatory courses per employee position.
4. Employee receives email with a secure access token/link.
5. Employee reads PDF in a **server-gated timed viewer** — next page/section unlocks only after the server confirms enough accumulated *active* time; progress + audit persisted per enrollment (cross-device resume).
6. After reading, comprehension test (single correct answer). Up to 3 attempts; each attempt draws from a distinct question subset; failing restarts reading.
7. On pass: record result in expediente, enable printable PDF certificate, award initial badges/points.
8. Admin views expedientes and filters (e.g., "all who completed course X").

### Out of scope (MVP — explicit)
- Multi-tenant / platform super-admin / strict data isolation between companies.
- SMS / WhatsApp channels (email only).
- AI-assisted or AI-generated courses/tests (manual authoring only).
- Full gamification (levels, leaderboards, points economy) — only initial badges.
- Electronic signature / qualified-certificate validity on certificates.
- Rich individual-employee CRUD UI *(recommendation: Excel-only import for MVP; individual create deferred — see Open Questions).*

## 3. Compliance & Legal Assumptions (RGPD / LOPDGDD)

These MUST be recorded as explicit assumptions in the proposal. We are **not** lawyers; the product owner must confirm.

- **DNI storage.** DNI is personal data (RGPD Art.4(1); not an Art.9 special category, but high-identifiability). Storing it verbatim per the confirmed decision requires: a **lawful basis** (employment relationship / legal obligation to keep training records), a **privacy notice** to employees (transparency, Art.13/14), **data minimization & purpose limitation**, **security** (TLS in transit; encryption at rest — standard DB encryption, NOT "special" per decision but should still be stated), a **retention policy**, and honoring employee rights (access/erasure). *Assumption:* the company provides lawful basis + privacy notice and accepts DNI-as-identifier for the training record.
- **Certificate legal validity.** MVP certificate is a **printable PDF with NO electronic signature**. *Assumption:* it serves as an internal training record and formal/qualified legal validity is NOT required at MVP. If evidentiary weight is needed later, phase 2 should add e-signature/CSV (@firma-style) — flag as open question.
- **Reading-time integrity.** Server-gated minimum time prevents advancing faster than 3× average, but **cannot cryptographically prove human presence**. *Assumption:* "reasonable control" (server-authoritative gating + activity heartbeats + visibility checks + immutable audit log) is accepted by the company as fulfilling its internal due-diligence/training-evidence obligation. This is a control, not a guarantee.
- **Identity verification.** Employee access via emailed token/link. *Assumption:* email possession ≈ identity for MVP. Weak binding — flag risk; phase 2 may add code + DNI re-check or 2FA.
- **Audit logs.** Required across devices for compliance evidence. *Assumption:* append-only server-side log of reading/exam events; question whether tamper-evidence (WORM) is mandated.

## 4. Technology Stack Analysis

The decisive technical driver is the **server-authoritative reading-time gate + cross-device audit**, which forces a real backend. The PDF viewer is unavoidably client-side (PDF.js). So the question is *one full-stack codebase* vs *separate front/back*.

| Option | Pros | Cons | Complexity |
|--------|------|------|------------|
| **A. Next.js (App Router, TS) full-stack** | One TS codebase (React for viewer + server actions/route handlers for gating/audit); huge ecosystem: `pdfjs-dist`/`react-pdf` (viewer), `pdf-lib` (cert gen), `xlsx` (Excel), `nodemailer`+Resend (email), `next-intl` (i18n), Prisma+Postgres; easy EU-host deploy; SSR for admin screens. | Node backend (fine, but enforcement logic must be written carefully server-side); heavier framework than needed for pure API. | Medium |
| **B. Django (Python) + React SPA** | Python excels at Excel (`pandas`/`openpyxl`) and PDF (`reportlab`); strong admin; clear API/auth; if team is Python-strong this is very productive. | Two languages/codebases, two deploys; React viewer still needed; more boilerplate for an internal tool. | Medium-High |
| **C. React (Vite) SPA + FastAPI (Python)** | Clean separation; FastAPI great for the authoritative gate/test/cert APIs; Python Excel/PDF libs. | Two deploy units; more moving parts; CORS/auth wiring; overkill for a single-team internal tool. | High |
| **D. Laravel / Rails monolith** | Very productive monoliths; good PDF/Excel libs (`prawn`/`roo`, `barryvdh/dompdf`). | Smaller fit for a highly interactive JS PDF viewer; less common in this ecosystem; team familiarity risk. | Medium |

### Recommendation (proposal input — NOT locked)
**Option A: Next.js (App Router, TypeScript) full-stack + PostgreSQL (Prisma).** Rationale: one language/codebase reduces MVP surface for a small team; React is required anyway for the PDF.js viewer; server actions/route handlers host the authoritative time-gate and audit log; the ecosystem directly covers every MVP need (viewer, certs, Excel, email, i18n). Decision is a *proposal input* — finalize only after the Open Questions on team familiarity and hosting/data-residency are answered.

**Key library map (A):**
- Viewer: `pdfjs-dist` (or `react-pdf`) — page/section-gated, client component.
- Time-gate/audit: Next route handlers + Postgres tables (`enrollment_progress`, `reading_audit`).
- Cert gen: `pdf-lib` (lightweight, precise) — or Playwright HTML→PDF if layout-rich certs are wanted.
- Excel: `xlsx` (SheetJS) — parse client-side, validate server-side.
- Email: `nodemailer` + provider (Resend/SMTP).
- i18n: `next-intl` (Spanish default, structure ready).
- Validation/forms: `zod` + `react-hook-form`.
- Auth: session-based (Auth.js or lightweight cookie sessions) — admin password + employee magic-link/code.
- Gamification: domain logic + simple `badge`/`points` tables.

**Anti-skip architecture (stack-agnostic):** per enrollment, compute `minTimePerSection = sectionBaseReadingTime / 3`. Client sends activity heartbeats (with Page Visibility + interaction checks); server accumulates *validated active time*; "unlock next" is granted only by the server after `accumulated >= minTime`. Progress + audit events persist server-side keyed by enrollment → cross-device resume. Honest limitation: cannot fully prevent a scripted bypass; mitigations raise the bar and the audit log is the compliance artifact.

## 5. Affected Areas (to be built — greenfield)

- `app/(admin)/...` — admin screens (import, course CRUD, catalog, expedientes). *(new)*
- `app/(employee)/...` — token-gated reader + test + badge views. *(new)*
- `lib/reading-gate.ts` + route handlers — authoritative time gate + audit. *(new, critical)*
- `lib/certificate.ts` — PDF cert generation. *(new)*
- `lib/excel.ts` — employee import parse/validate. *(new)*
- `lib/email.ts` — notifications. *(new)*
- `prisma/schema.prisma` — Employee, Course, Section, Test/QuestionBank, Enrollment, Progress, Audit, Badge. *(new)*
- `openspec/specs/...` — delta specs from `sdd-spec`. *(new)*

## 6. Risks

- **Reading-time integrity is not absolute.** Server gating + audit is a control, not proof of human presence; compliance must accept this.
- **Weak identity binding** (email-only access) — risk of someone else completing training.
- **RGPD exposure from DNI** if encryption-at-rest, retention, or privacy notice are not implemented; lawful basis unconfirmed.
- **Certificate has no legal/e-signature weight** — may not satisfy formal evidentiary needs.
- **Stack choice hinges on team familiarity + hosting/data-residency** (RGPD) — not yet decided.
- **Excel import edge cases** (malformed DNI, encoding, duplicates) can block onboarding day.

## 7. Open Questions (must be answered by the proposal)

1. **Team language/framework familiarity** — is the team TS/React or Python? Finalizes stack A vs B.
2. **Hosting & data residency** — self-hosted EU / Vercel EU region? Affects RGPD and Node choice.
3. **Employee auth** — magic-link vs access code vs password; admin auth model.
4. **MVP employee creation** — Excel-only (recommended) vs also minimal individual create.
5. **Reading-time formula** — how is "average reading speed" baselined (words/char per page/section)? Per-course configurable? Exact 3× ceiling semantics.
6. **Fail/restart rule** — does failing an attempt always restart reading from the beginning for all 3 attempts?
7. **Certificate fields & retention** — exact content, legal headers, record retention period.
8. **Audit tamper-evidence** — does compliance require WORM/append-only immutable logs?
9. **Badge definitions** — which actions grant which initial badges.
10. **Email provider** — which sender/provider for notifications.

## 8. Ready for Proposal

**Yes — conditionally.** Scope, actors, out-of-scope, and compliance assumptions are tightened enough to write a proposal. The orchestrator should tell the user: (a) the recommended stack is Next.js full-stack but is *not locked* pending Q1 (team familiarity) and Q2 (hosting/residency); (b) the four compliance assumptions (DNI, certificate validity, reading-time integrity, identity) are recorded as assumptions the product owner must confirm; (c) resolve the 10 open questions (especially auth model, reading-time formula, and Excel-only vs individual create) before/within `sdd-propose`.

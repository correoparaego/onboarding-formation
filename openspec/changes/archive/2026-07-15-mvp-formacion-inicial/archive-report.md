# Archive Report — mvp-formacion-inicial

- **Change**: `mvp-formacion-inicial`
- **Archived**: 2026-07-15
- **Archived to**: `openspec/changes/archive/2026-07-15-mvp-formacion-inicial/`
- **Artifact store**: openspec (filesystem)
- **Mode**: Standard (strict_tdd: false)

## What Was Built

A single-company internal web application for mandatory employee onboarding/training, replacing manual/oral training that left no compliance evidence trail. The MVP delivers, end-to-end:

- **Admin**: Excel (.xlsx) employee import with per-row validation report (missing field / bad email / invalid DNI), verbatim DNI storage, and DNI dedupe; course CRUD (PDF + authored test/bank), position→catalog mapping, expediente filters, certificate generation.
- **Employee**: token-gated (single-use magic-link/code) timed PDF reader with server-authoritative reading gate, comprehension test (≤3 attempts, distinct deterministic subsets, fail→restart reading), initial badges.
- **Cross-cutting**: server-authoritative reading-time gate + append-only audit log (cross-device resume), email-only Spanish notifications, i18n scaffold (Spanish default).
- **AI-assisted authoring (in scope, BYO key)**: admin supplies their own OpenAI-compatible LLM key (stored encrypted at rest, never exposed to client/employee, never logged); guided course-content generation (mode A) and PDF→test generation (mode B); human-in-the-loop review before persistence; PII-exclusion guard so no employee DNI/name/email/phone reaches the LLM.

## Final Stack

- **Backend**: Django (Python) + Django REST framework, JSON API. Apps: `courses`, `employees`, `reading_gate`, `certificates`, `notifications`, `authentication`, `ai_generation`. ORM via Django.
- **Frontend**: React + Vite SPA (static EU host), `pdfjs-dist` section-gated viewer, `react-hook-form` + `zod`, `react-i18next` (es default).
- **Database**: PostgreSQL (Django ORM), EU-region managed.
- **Supporting libs**: `openpyxl`/`pandas` (import), `reportlab` (cert PDF), `PyPDF2` (PDF text extraction), `pytest`/`pytest-django` (tests), Playwright (opt-in E2E).
- **Hosting**: EU-region managed PaaS — Python host for Django + static EU host for the React build; email via Resend/SMTP (configurable, no code change to switch).
- **Tenancy**: single-tenant (MVP). No `tenant_id` column; models tenant-agnostic for phase-2.

## Scope

- In scope: Excel import, course CRUD + bank, position catalog, mandatory auto-enrollment, secure token access, server-gated timed reading, comprehension test, printable certificates, initial badges, expediente + filters, append-only audit, configurable email notifications, admin password session + employee magic-link, and **AI generation via bring-your-own (BYO) key** (guided content + PDF→test, human-in-the-loop, PII-exclusion).
- Out of scope (MVP): multi-tenant/super-admin, SMS/WhatsApp, full gamification, e-signature/qualified cert validity, individual employee CRUD UI, fully autonomous course generation from scratch.

## Verification Result

- **Verdict**: PASS (archive-ready). `verify-report.md` archive gate CLEARED.
- **Tests**: **56 tests** pass (`python manage.py test` → `Ran 56 tests ... OK`; `pytest -q` → 56 pass). `manage.py check` clean; `makemigrations --check` → no changes.
- **Tasks**: 57/57 implementation tasks `[x]` (tasks.md). All 13 capability specs pass their covering tests.
- **Coverage**: spec compliance matrix — all 13 capabilities compliant (employee-import, course-management, enrollment-assignment, secure-access, timed-reading, comprehension-test, authentication, ai-generation, certificate, badges, expediente, audit-log, notifications).
- **Non-blocking warnings (informational)**: W2 email transport not verified with a real provider (`console` default exercised); W3 E2E Playwright not executed (no browser in env); W4 real OpenAI-compatible client not exercised at runtime (`AI_USE_FAKE_LLM=True` in tests). Suggestions S1–S4 (e.g., case-sensitive DNI dedupe, CSRF exemption on `/api/auth/*` and `/api/import`, `TEST_PASS_THRESHOLD=1.0` product decision, `expediente_list` returns DNI to admins by design).

## Resolved W1 Debt (DNI crypto)

The previously-BLOCKING W1 item — DNI encryption used a FIXED zero nonce (AES-GCM nonce reuse), an insecure scheme — is **RESOLVED** in PR7 (`mvp/fix-w1-dni-crypto`):

- `encrypt_value` now uses a **fresh random 12-byte nonce per encryption** (`os.urandom`), prepended to the ciphertext; `decrypt_value` recovers it.
- Dedupe/uniqueness moved to a **deterministic HMAC** (`dni_lookup_hash` → `HashedDNILookupField.dni_lookup`, `unique=True`), so equal DNIs still collide correctly without a deterministic ciphertext.
- The DNI is still stored **verbatim on read** (`EncryptedDNIField.from_db_value` = `decrypt_value`); duplicate DNI imports are still rejected (via `dni_lookup`).
- Acceptance covered by 6 new tests in `employees/tests_crypto.py` (verbatim round-trip, distinct-ciphertext/same-lookup, model-level + import-level duplicate rejection, `_FIXED_NONCE` removed, legacy-ciphertext recoverable). All pass.
- No design decision contradicted; all spec-facing behaviors (verbatim DNI, encrypt-at-rest, dedupe) preserved. Test count went 50 → 56 (+6 from the W1 fix acceptance suite).

**No CRITICAL findings. No BLOCKING items remain.**

## Source of Truth Updated

The following specs were promoted (copied verbatim, all ADDED Requirements) into `openspec/specs/` as the new source of truth:

| Capability | Requirements | Action |
|---|---|---|
| employee-import | 4 | Created |
| course-management | 3 | Created |
| enrollment-assignment | 2 | Created |
| secure-access | 3 | Created |
| timed-reading | 4 | Created |
| comprehension-test | 5 | Created |
| certificate | 3 | Created |
| badges | 4 | Created |
| expediente | 3 | Created |
| audit-log | 4 | Created |
| notifications | 3 | Created |
| authentication | 4 | Created |
| ai-generation | 6 | Created |
| **Total** | **48** | **13 created** |

## Archive Contents (audit trail — preserved, never modified)

- `proposal.md` ✅
- `design.md` ✅
- `exploration.md` ✅
- `specs/` ✅ (13 capability delta specs)
- `tasks.md` ✅ (57/57 complete)
- `apply-progress.md` ✅ (PR1–PR6 + W1 fix in PR7)
- `verify-report.md` ✅ (PASS, archive-ready)
- `archive-report.md` ✅ (this file)

## SDD Cycle Status

**COMPLETE.** `mvp-formacion-inicial` is fully planned, implemented, verified, and archived. The active changes directory no longer contains this change. Ready for the next change.

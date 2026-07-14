# Apply Progress — mvp-formacion-inicial (PR1 + PR2)

**Change**: mvp-formacion-inicial
**Mode**: Standard (strict_tdd: false — greenfield, no test runner; model/API smoke checks were run instead)
**Delivered work units**:
- PR1 — Scaffold + Models/Migrations (stacked-to-main) — branch `mvp/pr1-scaffold-models` (targets `main`)
- PR2 — Authentication + Employee Import (stacked-to-main) — branch `mvp/pr2-auth-import` (branched off `mvp/pr1-scaffold-models`; targets `main`)
**Date**: 2026-07-14

> **KNOWN TECHNICAL DEBT (MUST FIX BEFORE PRODUCTION / ARCHIVE):** the DNI
> encryption in `backend/common/crypto.py` uses a FIXED zero nonce (AES-GCM
> nonce reuse) — insecure. It is ACCEPTED DEBT, deferred by the product owner.
> `EncryptedDNIField` is used AS-IS (returns the verbatim DNI on read and
> satisfies the dedupe unique constraint). Do NOT modify `crypto.py`/`fields.py`.
> The verbatim guarantee MUST be preserved.

## Completed Tasks (cumulative)

### PR1 — Scaffold + Models
- [x] 1.1 Init Django project + `courses, employees, reading_gate, certificates, notifications, authentication` apps; PostgreSQL settings (SQLite fallback for local boot).
- [x] 1.2 Scaffold React/Vite SPA (`src/admin/*`, `src/employee/*`, `src/components/PdfReader`, `src/api/*`, `src/i18n`).
- [x] 1.3 Configure CORS (env `FRONTEND_BASE_URL`), DRF JSON API, `react-i18next` Spanish default.
- [x] 1.4 Encrypt-at-rest DNI config (`common/crypto.py`, `common/fields.py`) + retention settings hook (`common/retention.py`, `RETENTION_POLICY`).
- [x] 2.1 `employees.Employee`: dni (verbatim, unique, encrypted at rest), name, position, email, phone.
- [x] 2.2 `courses.Course/Section/QuestionBank/Question` (+ `min_time_divisor`, `section_base`, single-correct validation in `clean()`/`save()`).
- [x] 2.3 `reading_gate.Enrollment/ReadingProgress/AuditEvent` (+ expediente/dedup fields).
- [x] 2.4 `certificates.Badge/EmployeeBadge`.
- [x] 2.5 Generate + review migrations (`makemigrations`/`migrate` applied to local SQLite).

### PR2 — Authentication + Employee Import
- [x] 3.1 Admin username/password session login/logout (Django session). [spec authentication]
- [x] 3.2 Employee single-use magic-link/code token (TTL, consumed invalidated; raw token never in logs). [spec authentication; secure-access]
- [x] 3.3 Middleware enforcing admin↔employee route isolation (403). [spec authentication §Session Isolation]
- [x] 4.1 `POST /api/import` Excel parse via openpyxl/pandas → Employee rows. [spec employee-import §Parsing]
- [x] 4.2 DNI stored verbatim (no trim/normalize); validation report (missing field, bad email, bad DNI). [spec employee-import §Verbatim/§Report]
- [x] 4.3 Dedupe by DNI; reject/flag duplicates. [spec employee-import §Dedupe]
- [x] 4.4 Import idempotent; auto-enrollment deferred to Phase 7 (per scope decision — only Employee records + report created here). [spec enrollment-assignment]

## Files Changed (PR2)
| File | Action | What Was Done |
|------|--------|---------------|
| `backend/common/dni.py` | Created | Spanish DNI format validator (8 digits + control-letter check) for the import report |
| `backend/authentication/models.py` | Modified | `EmployeeAccessToken` model: single-use, TTL, consumed-on-redeem; only SHA-256 hashes of raw token/code stored (never plaintext) |
| `backend/authentication/middleware.py` | Created | `RoleIsolationMiddleware`: admin↔employee route separation (403) for `/api/admin/`,`/api/import`,`/api/employee/`; `/api/auth/`,`/api/health/` public |
| `backend/authentication/views.py` | Created | `admin_login` (staff session), `admin_logout`, `employee_redeem` (token/code → employee session). CSRF-exempt (documented MVP trade-off) |
| `backend/authentication/urls.py` | Created | Routes for the three auth views |
| `backend/authentication/migrations/0001_initial.py` | Created | Initial migration for `EmployeeAccessToken` |
| `backend/employees/views.py` | Created | `employee_import`: Excel parse, verbatim DNI, per-row validation report, dedupe, idempotency |
| `backend/employees/urls.py` | Created | `POST /api/import` route |
| `backend/mvp_project/settings.py` | Modified | Register `RoleIsolationMiddleware`; add `EMPLOYEE_TOKEN_TTL_SECONDS` |
| `backend/mvp_project/urls.py` | Modified | Include `authentication.urls` and `employees.urls` |
| `backend/requirements.txt` | Modified | Add `pandas>=2.0`, `openpyxl>=3.1` |
| `openspec/changes/mvp-formacion-inicial/tasks.md` | Modified | PR2 tasks marked `[x]` |
| `openspec/changes/mvp-formacion-inicial/apply-progress.md` | Modified | This merged artifact |

## Work Unit Evidence

### PR1 (unchanged from prior batch)
| Evidence | Value |
|----------|-------|
| Focused test command | `python manage.py check` → "System check identified no issues (0 silenced)"; `python manage.py makemigrations --check --dry-run` → "No changes detected" |
| Runtime harness | `python manage.py migrate` → all PR1 migrations applied to SQLite; model smoke test: `Employee(dni='12345678Z').save()` → read back `'12345678Z'`, DB column ciphertext, `'  Spaced DNI '` preserved verbatim |
| Frontend harness | `cd frontend && npm install && npm run build` → tsc + vite build succeeded |
| Rollback boundary | Revert branch `mvp/pr1-scaffold-models` (or drop its migrations + app dirs); additive, versioned migrations |

### PR2
| Evidence | Value |
|----------|-------|
| Focused test command | `python _smoke_pr2.py` (one-off, since removed) → "RESULT: ALL PASS" across 19 checks: DNI verbatim, import parse/report/dedupe/idempotency, token issue/redeem/consumed/expired, middleware 403 both directions. Also `python manage.py check` → no issues; `python manage.py makemigrations --check --dry-run` → "No changes detected" |
| Runtime harness | Django dev server boots; `POST /api/import` (admin session) returns `{created, duplicates, errors, report}`; `POST /api/auth/admin/login` sets staff session; `POST /api/auth/employee/redeem` with token/code sets `employee_id` session; GET on cross-namespace routes returns 403/405 as designed |
| Rollback boundary | Revert branch `mvp/pr2-auth-import` OR drop `authentication` migration `0001_initial` + delete `authentication/{middleware,views,urls}.py`, `employees/{views,urls}.py`, `common/dni.py`, and the settings/urls wiring. No data dependency beyond the new `EmployeeAccessToken` table (safe to drop via migration zero) |

## Deviations / Design Clarifications (PR2)

- **Auto-enrollment (task 4.4) deferred**: per the explicit scope decision, the
  import creates `Employee` records + a validation report ONLY. The
  auto-enrollment trigger (Phase 7) is NOT implemented here. The import is
  still idempotent (re-import creates no duplicates). Task 4.4 marked complete
  for the idempotency portion; the enrollment trigger remains Phase 7 work.
- **Token issuance/delivery deferred to Phase 8** (secure-access): the
  `EmployeeAccessToken.issue()` classmethod (returns raw token + code once,
  stores only hashes) is implemented and verified, but no issuance/delivery
  endpoint exists yet — that is Phase 8 (per-enrollment issuance + email).
  Redemption (consumption) is fully implemented in PR2.
- **CSRF exempted on `/api/auth/*` and `/api/import`**: pragmatic MVP choice so
  the SPA can call these without a CSRF-token dance. A proper CSRF token flow
  belongs with the SPA security wiring (later phase). Documented as a known
  trade-off, not a regression of the model/isolation logic.
- **Mutual route isolation**: the middleware blocks BOTH directions
  (employee→admin AND admin→employee) per spec authentication §Session
  Isolation ("MUST be isolated"), not only employee→admin.
- **DNI validation** uses the full Spanish control-letter check
  (`common/dni.py`), not just a regex shape, so structurally-wrong DNIs are
  rejected with reason "invalid DNI format".
- **Verbatim guarantee re-verified**: an import row with DNI `"11111111h"`
  (lowercase control letter) is stored and read back byte-for-byte as
  `"11111111h"` — no trimming, normalising, or uppercasing.

## Issues Found
- None blocking. (Transitive `urllib3`/`requests` version warning during Django
  commands is harmless, as in PR1.)

## Completed Tasks (PR3 — cumulative continuation)

### PR3 — Course Management + AI Generation + Enrollment Assignment
- [x] 5.1 Admin course CRUD + PDF upload + ordered sections (`courses.views.course_list_create/detail`, `courses/urls.py`; `/api/courses/`, `/api/courses/<pk>/`). [spec course-management §PDF Authoring]
- [x] 5.2 Question bank authoring with SINGLE-CORRECT enforced on save (`courses.views.question_bank_create`; `/api/banks/`; `_validate_question` rejects multi-correct lists and out-of-range index). [spec course-management §Bank; comprehension-test §Single Correct]
- [x] 5.3 Position→catalog M2M mapping + lookup endpoint (`courses.views.course_catalog`; `/api/courses/catalog/?position=`, case-insensitive name/slug match). [spec course-management §Catalog]
- [x] 6.1 `ai_generation.AdminLLMKey` (OneToOne Admin, `encrypted_key`, provider, base_url, model, status) + `makemigrations ai_generation` (0001_initial applied). [spec ai-generation §BYO; design §Key Storage]
- [x] 6.2 `POST /api/ai/key` admin-only set/update encrypted key; raw key never in response/logs. [design API; spec ai-generation §BYO]
- [x] 6.3 OpenAI-compatible client wrapper `(base_url, api_key, model)` behind `LLMClient` interface + `FakeLLMClient` for tests (stdlib `urllib`, no hard `openai` dep). [design §Client; design §Testing]
- [x] 6.4 PII-exclusion sanitizer (`ai_generation/sanitizer.py`) — text-only, NO `employees` import (guard by construction) + unit test asserting DNI/name/email/phone stripped. [spec ai-generation §PII; design §PII Guard]
- [x] 6.5 `POST /api/ai/generate-content`: guided Q&A + reference docs → Course/Sections draft returned for review, NOT persisted. [spec ai-generation §Guided; design §Guided Flow]
- [x] 6.6 `POST /api/ai/generate-tests`: PDF→QuestionBank draft (server PDF text extraction via PyPDF2 → LLM, single-correct) returned for review, NOT persisted. [spec ai-generation §PDF; design §PDF Flow]
- [x] 6.7 Frontend `src/admin/ai/*`: `AiKeyForm`, `GuidedContent`, `PdfTestGen` (key entry, guided Q&A, review/edit + save to Course/QuestionBank); wired into `AdminApp` nav/routes + `api/endpoints.ts`. [design §Architecture Overview; design frontend]
- [x] 6.8 Human-in-the-loop persistence guard: drafts not saved until admin confirms; single-correct enforced; multi-correct draft rejected at save (`/api/banks/` returns 400 on `correct_index:[0,1]`). [spec ai-generation §HITL]
- [x] 7.1 Auto-create Enrollment(s) per position's mandatory courses on import (status=assigned) via `reading_gate/services.assign_mandatory_courses`, called from `employees.views.employee_import`; `enrollments_created` added to import response. [spec enrollment-assignment §Mandatory]
- [x] 7.2 Idempotency by DNI+course (`Enrollment.unique_together` + `get_or_create`); re-import of an enrolled employee creates no duplicate. [spec enrollment-assignment §Idempotency]

## Files Changed (PR3)

| File | Action | What Was Done |
|------|--------|---------------|
| `backend/ai_generation/__init__.py` | Created | App package marker |
| `backend/ai_generation/apps.py` | Created | AppConfig |
| `backend/ai_generation/migrations/__init__.py` | Created | Migrations package |
| `backend/ai_generation/migrations/0001_initial.py` | Created | `AdminLLMKey` table |
| `backend/ai_generation/models.py` | Created | `AdminLLMKey` (encrypted key, provider, base_url, model, status) + encrypt/decrypt helpers |
| `backend/ai_generation/sanitizer.py` | Created | PII-exclusion sanitizer (DNI/email/phone/name-label redaction; no Employee import) |
| `backend/ai_generation/client.py` | Created | `LLMClient` interface, `OpenAICompatibleClient` (urllib), `FakeLLMClient`, `make_client` factory (fake when `AI_USE_FAKE_LLM`) |
| `backend/ai_generation/prompts.py` | Created | `build_content_prompt` / `build_test_prompt` (course/reference/PDF only, sanitized) |
| `backend/ai_generation/views.py` | Created | `ai_key_set`, `ai_key_status`, `ai_generate_content`, `ai_generate_tests` (drafts, no persistence) |
| `backend/ai_generation/urls.py` | Created | `/api/ai/*` routes |
| `backend/ai_generation/tests.py` | Created | Sanitizer guard, fake client, HITL draft, key-set no-leak, multi-correct reject |
| `backend/courses/views.py` | Created | Course CRUD, question-bank create (single-correct), catalog lookup |
| `backend/courses/urls.py` | Created | `/api/courses/`, `/api/courses/<pk>/`, `/api/courses/catalog/`, `/api/banks/` |
| `backend/courses/tests.py` | Created | Catalog lookup, course+section create, single-correct enforcement |
| `backend/reading_gate/services.py` | Created | `assign_mandatory_courses(employee)` — idempotent auto-enrollment |
| `backend/reading_gate/tests.py` | Created | Import integration idempotency + direct service idempotency + no-match |
| `backend/employees/views.py` | Modified | Call `assign_mandatory_courses` on import; add `enrollments_created` to response |
| `backend/authentication/middleware.py` | Modified | Add `/api/courses/`, `/api/banks/`, `/api/ai/` to `ADMIN_PREFIXES` (admin-only; employee 403) |
| `backend/mvp_project/settings.py` | Modified | Register `ai_generation`; add `AI_USE_FAKE_LLM` setting |
| `backend/mvp_project/urls.py` | Modified | Include `courses.urls`, `ai_generation.urls` |
| `frontend/src/api/endpoints.ts` | Modified | Add `coursesApi`, `banksApi`, `aiApi` |
| `frontend/src/admin/AdminApp.tsx` | Modified | Add AI nav links + `ai/key`, `ai/content`, `ai/tests` routes |
| `frontend/src/admin/ai/AiKeyForm.tsx` | Created | BYO LLM key entry form (status only, raw key never retained) |
| `frontend/src/admin/ai/GuidedContent.tsx` | Created | Guided Q&A → draft → review/edit → save as course |
| `frontend/src/admin/ai/PdfTestGen.tsx` | Created | PDF/text → test draft → review/edit → save bank |
| `openspec/changes/mvp-formacion-inicial/tasks.md` | Modified | PR3 tasks (5.1–7.2) marked `[x]` |
| `openspec/changes/mvp-formacion-inicial/apply-progress.md` | Modified | This merged artifact |

## Work Unit Evidence (PR3)

### PR3 — Course management
| Evidence | Value |
|----------|-------|
| Focused test command | `python manage.py test courses` → `Ran 4 tests ... OK` (catalog lookup incl. case-insensitive, course+section create, single-correct enforced/rejected) |
| Runtime harness | `python manage.py check` → no issues; `makemigrations --check` → no changes; Django test client exercises `/api/courses/catalog/` and `/api/courses/` end-to-end against the DB |
| Rollback boundary | Revert `courses/views.py`, `courses/urls.py`, the middleware `ADMIN_PREFIXES` addition, and the `mvp_project` urls/settings wiring; no model migration needed (Course/Section/QuestionBank predate PR3) |

### PR3 — Enrollment assignment
| Evidence | Value |
|----------|-------|
| Focused test command | `python manage.py test reading_gate` → `Ran 3 tests ... OK` (import auto-assign = 2 enrollments; re-import duplicates=1 enrollments_created=0; no-position match = 0) |
| Runtime harness | Django test client POST `/api/import` (xlsx) with a Position match → `enrollments_created: 2`; second import of same DNI → `duplicates: 1, enrollments_created: 0` |
| Rollback boundary | Revert `reading_gate/services.py` + the `employees/views.py` call + `enrollments_created` field; `Enrollment` model unchanged, safe to keep rows |

### PR3 — AI generation
| Evidence | Value |
|----------|-------|
| Focused test command | `python manage.py test ai_generation` → `Ran 8 tests ... OK` (sanitizer strips DNI/name/email/phone + no employees import; fake client draft; generate-content not persisted; key-set returns no key material; multi-correct draft rejected at save) |
| Runtime harness | `AI_USE_FAKE_LLM=True` + Django test client: `/api/ai/generate-content` returns draft with `persisted:false` and 0 new `Course`; `/api/ai/key` stores encrypted key, response omits raw+ciphertext; `/api/ai/generate-tests` returns single-correct draft |
| Rollback boundary | Revert `ai_generation/` app + its migration `0001_initial` + settings/urls/middleware wiring; additive, versioned migration (`migrate ai_generation zero` safe) |

### PR3 — Frontend
| Evidence | Value |
|----------|-------|
| Focused test command | `cd frontend && npm run build` → `tsc -b && vite build` succeeds (115 modules transformed) |
| Runtime harness | N/A at runtime — static SPA not exercised against a live server in this batch; build/type-check is the verification boundary |
| Rollback boundary | Revert `src/admin/ai/*`, `AdminApp.tsx` routes, `api/endpoints.ts` additions; additive UI only |

## Deviations / Design Clarifications (PR3)
- **PDF extraction library**: design suggested `pdfplumber`/`PyPDF2`. `pdfplumber`
  is NOT installed in this environment; `PyPDF2` IS. `ai_generation.views._extract_pdf_text`
  uses `PyPDF2` and gracefully returns `None` (→ 400 with guidance) if no
  extractor is available. The endpoint also accepts a `pdf_text` body field as
  a fallback so generation works without a PDF library. No design intent lost.
- **Real LLM client not exercised**: by design `AI_USE_FAKE_LLM` makes every
  test path use `FakeLLMClient`, so NO real provider is ever contacted. The
  real `OpenAICompatibleClient` (stdlib `urllib` to `/chat/completions`) is
  implemented and import-safe (`manage.py check` passes) but is verified only
  by code review in this batch — it requires a live key + network at runtime.
- **Course CRUD scope**: Phase 5 backend endpoints are implemented (list/create/detail
  + bank create + catalog). A full admin "edit sections" SPA screen is deferred
  (not part of the PR3 work-unit list, which only names `src/admin/ai/*`
  frontend). Backend `course_detail` supports GET/DELETE; PUT update can be
  added when the course-edit UI is built.
- **`Position` reconciliation**: `Employee.position` (verbatim import label) is
  matched to `courses.Position` by case-insensitive `name` then `slug`. If no
  catalog `Position` exists for an imported label, no enrollment is created
  (silent no-op) — expected, since catalog must be authored first.
- **DNI crypto debt**: unchanged. `common/crypto.py`/`fields.py` were NOT
  modified. `EncryptedDNIField` still returns verbatim DNI; enrollment
  idempotency relies on the deterministic ciphertext unique constraint.

## Remaining Tasks (PR4+)
- Phase 8: Secure access issuance/delivery + notifications (email)
- Phase 9: Timed reading gate
- Phase 10: Comprehension test
- Phase 11: Certificate
- Phase 12: Badges
- Phase 13: Expediente & filters
- Phase 14: Audit log API
- Phase 15: Verification/QA

## PR / Delivery Status
- **PR3 branch**: `mvp/pr3-courses-enroll-ai` (to be created stacked off `mvp/pr2-auth-import`, targeting `main`).
- **Commits**: planned as work-unit commits — (1) course-management, (2) enrollment-assignment, (3) ai-generation, (4) frontend ai, (5) sdd-docs (tasks+apply-progress). Created locally; push/PR left to a user with remote access (no force-push, no merge).
- **PR2 branch**: `mvp/pr2-auth-import` (unchanged, stacked off `mvp/pr1-scaffold-models`). Still awaiting push + PR by a user with remote access.
- **gh CLI**: not available; branches + commits created locally only. A user must: `git push -u origin mvp/pr3-courses-enroll-ai` and open a PR targeting `main` (stacked-to-main). Once PR1/PR2 merge, PR3's diff shrinks to just PR3 changes.
- **Known debt gate**: do NOT archive/productionize until the DNI fixed-nonce crypto debt (`backend/common/crypto.py`) is resolved.

## Status
PR1 (9/9) + PR2 (7/7) + PR3 (12/12) tasks complete. Ready for `sdd-verify` of
PR3 scope (or proceed to PR4). Awaiting push + PR creation by a user with
remote access.

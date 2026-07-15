# Apply Progress — mvp-formacion-inicial (PR1 + PR2 + PR3 + PR4)

**Change**: mvp-formacion-inicial
**Mode**: Standard (strict_tdd: false; Django `manage.py test` used for focused unit/integration checks — 15 tests pass for the reading_gate app)
**Delivered work units**:
- PR1 — Scaffold + Models/Migrations (stacked-to-main) — branch `mvp/pr1-scaffold-models` (targets `main`)
- PR2 — Authentication + Employee Import (stacked-to-main) — branch `mvp/pr2-auth-import` (branched off `mvp/pr1-scaffold-models`; targets `main`)
- PR3 — Course Management + AI Generation + Enrollment (stacked-to-main) — branch `mvp/pr3-courses-enroll-ai` (off `mvp/pr2-auth-import`; targets `main`)
- PR4 — Timed Reading Gate + Comprehension Test + immediate Audit (stacked-to-main) — branch `mvp/pr4-reading-test` (off `mvp/pr3-courses-enroll-ai`; targets `main`)
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

### PR4 — Timed Reading Gate + Comprehension Test (stacked-to-main)
> NOTE ON PHASE NUMBERING: the orchestrator relabelled these as "Phase 8: Timed
> Reading Gate (8.1–8.4)" and "Phase 9: Comprehension Test (9.1–9.4)". They map
> 1:1 to tasks.md **Phase 9 (Timed Reading Gate, 9.1–9.4)** and **Phase 10
> (Comprehension Test, 10.1–10.4)** — both marked `[x]` there. The work unit is
> the "Timed gate + test" PR4 slice from the Review Workload Forecast.
- [x] 9.1 `POST /api/reading/heartbeat`: validate visibility+interaction, credit delta (server-authoritative; client heartbeats are untrusted input). [spec timed-reading §Heartbeat; design §Sequence]
- [x] 9.2 Server gate: unlock next section ONLY when accumulated ≥ `section_base / min_time_divisor`; section 1 always open; previous-section-complete enforced. [spec timed-reading §Server-Gated]
- [x] 9.3 `ReadingProgress` per (enrollment, section); cross-device resume keyed by enrollment; `device_id`/`session_id` captured. [spec timed-reading §Cross-Device]
- [x] 9.4 All sections pass → `Enrollment.status=complete`, test unlocks. [spec timed-reading §Completion]
- [x] 10.1 `POST /api/test/submit`: grade attempt; ≤3 attempts; 4th blocked → `failed_exhausted`. [spec comprehension-test §Max Three]
- [x] 10.2 Deterministic DISTINCT subset per attempt via `seed=sha256(enrollment_id, attempt_no)` shuffle of the QuestionBank (NOT Python's salted `hash`). [spec comprehension-test §Distinct; design §Test Flow]
- [x] 10.3 Fail resets `ReadingProgress` to section 1 / 0s (rows deleted) and increments `attempts_used`. [spec comprehension-test §Fail Restart]
- [x] 10.4 Pass → `Enrollment.status=passed` (cert + badge evaluation deferred to later phases). [spec comprehension-test §Pass]
- [x] Audit (immediate, gate/test-produced events only): `section_complete`, `reading_complete`, `attempt_start`, `attempt_submit`, `attempt_fail`, `attempt_blocked` written to the append-only `AuditEvent` keyed by enrollment — NO DNI/raw token in payloads. (Full audit coverage/wiring remains PR6.)

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

## Files Changed (PR4)
| File | Action | What Was Done |
|------|--------|---------------|
| `backend/reading_gate/services.py` | Modified | Added `process_heartbeat` (sequential unlock gate, visibility+interaction credit, delta clamp, all-sections-complete → status=complete), `get_test_subset` (sha256-deterministic distinct subset), `get_test_questions` (attempt view, withholds `correct_index`, emits `attempt_start`), `grade_submission` (≤3 attempts, 4th blocked→`failed_exhausted`, fail resets reading, pass→`passed`), `_audit` helper (append-only, no PII). Kept `assign_mandatory_courses`. Added tunable constants `MAX_HEARTBEAT_DELTA`, `TEST_SUBSET_SIZE`, `TEST_PASS_THRESHOLD`. |
| `backend/reading_gate/views.py` | Created | `reading_heartbeat` (POST), `test_questions` (GET), `test_submit` (POST). Employee-only via `request.session["employee_id"]`; enrollment ownership enforced (404 if not owned). |
| `backend/reading_gate/urls.py` | Created | Routes `/api/reading/heartbeat`, `/api/test/questions`, `/api/test/submit`. |
| `backend/authentication/middleware.py` | Modified | Added `/api/reading/` and `/api/test/` to `EMPLOYEE_PREFIXES` (employee-only; admin→403). |
| `backend/mvp_project/urls.py` | Modified | Included `reading_gate.urls`. |
| `backend/reading_gate/tests.py` | Modified | Added `ReadingGateTests` (4), `ComprehensionTestTests` (5), `ReadingGateAuthzTests` (3) — 12 new tests. |
| `openspec/changes/mvp-formacion-inicial/tasks.md` | Modified | Phase 9 (9.1–9.4) + Phase 10 (10.1–10.4) marked `[x]`. |
| `openspec/changes/mvp-formacion-inicial/apply-progress.md` | Modified | This merged artifact. |

## Work Unit Evidence (PR4)

### PR4 — Timed reading gate
| Evidence | Value |
|----------|-------|
| Focused test command | `python manage.py test reading_gate` → `Ran 15 tests in 1.0s ... OK` (3 enrollment-assignment + 4 gate + 5 comprehension + 3 authz). Gate tests assert: section 2 locked until section 1 complete; visibility+interaction required to credit; delta clamped to 120s; negative delta ignored; all-sections-complete → status=complete + `section_complete`/`reading_complete` audit events. |
| Runtime harness | `python manage.py check` → "System check identified no issues (0 silenced)". Django test client POST `/api/reading/heartbeat` (employee session) accumulates 30s and reports `section_complete:true`; wrong-employee session → 404; no session → 403. |
| Rollback boundary | Revert `reading_gate/views.py`, `reading_gate/urls.py`, the middleware `EMPLOYEE_PREFIXES` addition, and the `mvp_project/urls.py` include. No model/migration change (all fields pre-existed in PR1/2), so nothing to migrate down. |

### PR4 — Comprehension test + audit
| Evidence | Value |
|----------|-------|
| Focused test command | Same `python manage.py test reading_gate` run (above). Comprehension tests assert: subset deterministic per attempt AND distinct across attempts; pass → status=passed (attempts_used=1); fail → ReadingProgress deleted + status=in_progress + `attempt_fail` audit; 4th attempt (attempts_used=3) → 409 + status=`failed_exhausted` + `attempt_blocked` audit; `get_test_questions` withholds `correct_index` and emits `attempt_start`. |
| Runtime harness | `python manage.py check` clean; Django test client exercised the full gate→unlock→test path against the SQLite test DB. |
| Rollback boundary | Revert `reading_gate/services.py` gate/test functions + `views.py`/`urls.py` + middleware/urls wiring. The only new persisted rows are `AuditEvent` (append-only, harmless to retain) — no schema change, so `migrate reading_gate zero` is NOT required. |

## Deviations / Design Clarifications (PR4)
- **Pass threshold = 100% correct** (`TEST_PASS_THRESHOLD = 1.0`): the spec
  defines single-correct answers and "Pass → status=passed" but does NOT state a
  passing fraction. For a compliance onboarding gate, requiring every answered
  question correct is the safe default. It is a single named constant, trivially
  tunable by the product owner. Documented as an open product decision.
- **Subset size**: `TEST_SUBSET_SIZE = 5`. The bank is shuffled by a
  `sha256(enrollment_id, attempt_no)` seed and the first 5 taken; when the bank
  holds >5 questions, different attempts draw genuinely DISTINCT subsets. With
  ≤5 questions the whole bank is used (still deterministically ordered per
  attempt). `seed` uses SHA-256, NOT Python's salted `hash()`, so subsets are
  stable across processes/restarts (determinism requirement satisfied).
- **Heartbeat delta clamp**: untrusted client input is clamped to
  `MAX_HEARTBEAT_DELTA = 120s` per heartbeat to bound time-inflation fraud; a
  negative/non-int delta credits 0. This is "reasonable control" (RGPD 3), not
  human-presence proof — as the design explicitly accepts.
- **`GET /api/test/questions` added** (not in the literal task list, which only
  names `POST /api/test/submit`): the comprehension flow must SHOW questions
  before grading, so a deterministic, `correct_index`-withholding fetch endpoint
  is required. It does NOT consume an attempt (only `submit` increments
  `attempts_used`) and emits `attempt_start`. This is in-scope for the
  "Comprehension Test" work unit.
- **Audit is partial by design**: only the events the gate/test naturally
  produce (`section_complete`, `reading_complete`, `attempt_start`,
  `attempt_submit`, `attempt_fail`, `attempt_blocked`) are emitted. The formal
  append-only API and full coverage (incl. cert issuance) remain PR6. Payloads
  reference `enrollment_id` + metadata ONLY — NO DNI, token, or PII.
- **No model changes / no new migration**: `Enrollment` (status/attempts_used),
  `ReadingProgress` (accumulated_time/reached_section/device_id/session_id), and
  `AuditEvent` already existed from PR1/2. PR4 is pure API + service logic.
- **DNI crypto debt**: unchanged. `common/crypto.py`/`fields.py` were NOT
  touched. Verbatim DNI guarantee preserved; enrollment ownership is checked via
  `employee_id` from the session, never from request bodies.

## Remaining Tasks (PR5+)
- Phase 8: Secure access issuance/delivery + notifications (email)
- Phase 11: Certificate
- Phase 12: Badges
- Phase 13: Expediente & filters
- Phase 14: Audit log API (formal append-only API + full coverage)
- Phase 15: Verification/QA

## PR / Delivery Status
- **PR4 branch**: `mvp/pr4-reading-test` (created stacked off `mvp/pr3-courses-enroll-ai`, targeting `main`). [chain strategy: stacked-to-main]
- **Commits**: work-unit commits (created locally; push/PR left to a user with remote access, no force-push/no merge): (1) `feat(reading)` backend impl — server-authoritative reading gate + comprehension test + audit (services/views/urls/middleware/project-urls); (2) `test(reading)` — gate math, subset determinism, fail→restart, attempt cap, authz (15 tests); (3) `docs(sdd)` — tasks.md `[x]` + merged apply-progress. The gate/test/audit logic shares `services.py`/`views.py`, so they are committed together as one coherent backend unit rather than split via hunk-staging.
- **Prior branches**: `mvp/pr1-scaffold-models`, `mvp/pr2-auth-import`, `mvp/pr3-courses-enroll-ai` — all still awaiting push + PR by a user with remote access. `gh` CLI is not available; branches + commits are local only.
- **Known debt gate**: do NOT archive/productionize until the DNI fixed-nonce crypto debt (`backend/common/crypto.py`) is resolved.

## Status
PR1 (9/9) + PR2 (7/7) + PR3 (12/12) tasks complete. Ready for `sdd-verify` of
PR3 scope (or proceed to PR4). Awaiting push + PR creation by a
user with remote access.

# ─────────────────────────────────────────────────────────────────────────────
# PR5 — Secure Access + Certificate + Badges + Expediente (stacked-to-main)
# ─────────────────────────────────────────────────────────────────────────────
**Change**: mvp-formacion-inicial
**Mode**: Standard (strict_tdd: false; Django `manage.py test` used for focused unit/integration checks — 13 new PR5 tests pass)
**Branch**: `mvp/pr5-secure-cert-badges-expediente` (created stacked off `mvp/pr4-reading-test`, targeting `main`) — [chain strategy: stacked-to-main]
**Date**: 2026-07-15

> **KNOWN TECHNICAL DEBT (STILL OPEN / MUST FIX BEFORE PRODUCTION OR ARCHIVE):**
> the DNI encryption in `backend/common/crypto.py` uses a FIXED zero nonce
> (AES-GCM nonce reuse) — insecure. It is ACCEPTED DEBT, deferred by the product
> owner. `EncryptedDNIField` is used AS-IS (returns the verbatim DNI on read and
> satisfies the dedupe unique constraint). PR5 did NOT modify `crypto.py`/
> `fields.py`. The verbatim guarantee is preserved (certificate prints DNI
> verbatim, verified via PyPDF2 text extraction). Do NOT modify crypto until the
> debt is fixed.

## Completed Tasks (PR5 — cumulative continuation)

### PR5 — Secure Access & Notifications (Phase 8, tasks 8.1–8.4)
- [x] 8.1 Token issuance per pending enrollment (single-use, TTL) on assignment — reuses `EmployeeAccessToken.issue()` from PR2; issued inside `assign_mandatory_courses` for each NEW enrollment and via the admin resend endpoint. [spec secure-access §Issuance]
- [x] 8.2 Token consumption invalidation + reuse block — satisfied by PR2's `EmployeeAccessToken.redeem()` (sets `consumed_at`; reused token → "consumed"). No new code in PR5; verified by PR2 tests + this PR's issuance/resend tests. [spec secure-access §Consumption]
- [x] 8.3 Configurable email transport (Resend/SMTP/console) + Spanish templates (access/reminder/completion). [spec notifications]
- [x] 8.4 Delivery logging (recipient/status, no raw token/secrets) via `NotificationLog`. [spec notifications §Logging]

### PR5 — Certificate (Phase 11, tasks 11.1–11.2)
- [x] 11.1 `GET /api/certificate/<enrollment>` (admin-only): reportlab PDF with name, DNI verbatim, date, course title, evaluation, summary index. [spec certificate]
- [x] 11.2 One active `Certificate` per passed enrollment (`OneToOne`); regeneration deterministic — `core_fields_hash` identical across regenerations. [spec certificate §One Per]

### PR5 — Badges (Phase 12, tasks 12.1–12.2)
- [x] 12.1 Seed initial badges ("Primer curso", "Catálogo completo", "Sin fallos") via data migration `0003_seed_badges` (+ defensive `ensure_badges()`). [spec badges §Initial Set]
- [x] 12.2 Award logic on pass: `award_badges_on_pass` → first course, clean first attempt, all-position mandatory courses passed (idempotent via `EmployeeBadge` unique_together). [spec badges §Award*]

### PR5 — Expediente & Filters (Phase 13, tasks 13.1–13.3)
- [x] 13.1 Persist per-enrollment result (`Expediente`: status, attempts, score, dates) on pass and on exhaustion. [spec expediente §Storage]
- [x] 13.2 Admin filter `GET /api/expediente?course=&status=`. [spec expediente §Filter]
- [x] 13.3 Retention policy hook (`get_retention_policy`); records are never purged by app rollback (no delete code). [spec expediente §Retention]

## Files Changed (PR5)
| File | Action | What Was Done |
|------|--------|---------------|
| `backend/notifications/models.py` | Rewritten | `NotificationLog` (recipient, template, channel, status, detail — NO token/secret) |
| `backend/notifications/transports.py` | Created | `ConsoleEmailTransport` (default), `SMTPEmailTransport` (Django send_mail), `ResendEmailTransport` (lazy `resend` import); `get_transport()` from `EMAIL_TRANSPORT` |
| `backend/notifications/templates.py` | Created | Spanish `access_email` / `reminder_email` / `completion_email` (magic-link built from `FRONTEND_BASE_URL`) |
| `backend/notifications/services.py` | Created | `issue_access_token`, `resend_access_token` (idempotent single-active-token), `send_reminder`, `send_completion` — best-effort, never logs raw secret |
| `backend/notifications/views.py` | Created | `admin_resend_access` (admin-only; does NOT echo raw token/code) |
| `backend/notifications/urls.py` | Created | `POST /api/admin/enrollment/<pk>/resend-access` |
| `backend/notifications/migrations/0001_initial.py` | Created | `NotificationLog` table |
| `backend/certificates/models.py` | Modified | Added `Certificate` model (`OneToOne` enrollment, `core_fields_hash`) |
| `backend/certificates/services.py` | Created | `generate_certificate_pdf` (reportlab, lazy import), `award_badges_on_pass`, `ensure_badges`, `_core_fields`/`_core_hash` |
| `backend/certificates/views.py` | Created | `certificate_pdf` (admin-only; 409 if not passed) |
| `backend/certificates/urls.py` | Created | `GET /api/certificate/<pk>` |
| `backend/certificates/migrations/0002_certificate.py` | Created | `Certificate` table |
| `backend/certificates/migrations/0003_seed_badges.py` | Created | Data migration seeding the 3 initial badges |
| `backend/reading_gate/models.py` | Modified | Added `Expediente` model (status, attempts, score, total, completed_at, retention hook) |
| `backend/reading_gate/services.py` | Modified | Issuance on assignment in `assign_mandatory_courses`; `_write_expediente` + `_on_pass` (expediente + badges + completion) on pass/exhaustion |
| `backend/reading_gate/views.py` | Modified | `expediente_list` admin filter |
| `backend/reading_gate/urls.py` | Modified | `GET /api/expediente` route |
| `backend/reading_gate/migrations/0002_expediente.py` | Created | `Expediente` table |
| `backend/authentication/middleware.py` | Modified | `ADMIN_PREFIXES` += `/api/certificate/`, `/api/expediente/` (admin-only) |
| `backend/mvp_project/urls.py` | Modified | Include `notifications.urls`, `certificates.urls` |
| `backend/mvp_project/settings.py` | Modified | `EMAIL_TRANSPORT` (default `console`), `DEFAULT_FROM_EMAIL`, `RESEND_API_KEY` |
| `backend/requirements.txt` | Modified | Add `reportlab>=4.0`, optional `resend` |
| `backend/notifications/tests.py` | Created | 5 tests: transport config, issuance+log-no-secret, idempotent resend, no-email skip, resend endpoint |
| `backend/certificates/tests.py` | Created | 4 tests: badge seed, PDF verbatim DNI/title, one-cert+idempotent hash, cert view requires passed |
| `backend/reading_gate/tests.py` | Modified | + `ExpedienteAndBadgesTests` (pass writes expediente + awards primer-curso/sin-fallos; admin filter) |
| `openspec/changes/mvp-formacion-inicial/tasks.md` | Modified | PR5 tasks (8.1–8.4, 11.1–11.2, 12.1–12.2, 13.1–13.3) marked `[x]`; chain strategy resolved |
| `openspec/changes/mvp-formacion-inicial/apply-progress.md` | Modified | This merged artifact |

## Work Unit Evidence (PR5)

### PR5 — Secure Access & Notifications
| Evidence | Value |
|----------|-------|
| Focused test command | `python manage.py test notifications` → `Ran 5 tests ... OK` (console transport default; issuance creates `EmployeeAccessToken` with only hashes; `NotificationLog` recipient+status present; raw token/code absent from log; resend leaves exactly ONE unconsumed token; resend endpoint returns ok without token/code in body) |
| Runtime harness | `python manage.py check` clean; Django test client `POST /api/admin/enrollment/<pk>/resend-access` (admin session) → 200 `{"ok":true,"employee":...}`; console transport prints the Spanish magic-link email to stdout; `NotificationLog` row shows recipient+status, never the raw token |
| Rollback boundary | Revert `notifications/` (models/services/views/urls/transports/templates) + middleware `ADMIN_PREFIXES` additions + `mvp_project` urls/settings; `migrate notifications zero` drops `NotificationLog` (additive migration) |

### PR5 — Certificate
| Evidence | Value |
|----------|-------|
| Focused test command | `python manage.py test certificates` → `Ran 4 tests ... OK` (badge seed; PDF contains verbatim `12345678Z` + `Curso A` + evaluation via PyPDF2 text extraction; one `Certificate` per enrollment; regeneration `core_fields_hash` identical; view returns `application/pdf` and 409 for non-passed) |
| Runtime harness | Django test client `GET /api/certificate/<pk>` (admin session) → 200 `application/pdf`; content extracted via PyPDF2 contains the verbatim DNI; `GET` on a non-`passed` enrollment → 409 |
| Rollback boundary | Revert `certificates/services.py`, `views.py`, `urls.py` + middleware `ADMIN_PREFIXES` + project urls include + settings email block; `migrate certificates zero` drops `Certificate` (and reverts `0003_seed_badges` deleting seeded badges — keep `0003` if badges must survive a cert-only revert) |

### PR5 — Badges
| Evidence | Value |
|----------|-------|
| Focused test command | Same `certificates` run (badge seed) + `reading_gate` `ExpedienteAndBadgesTests` → first pass awards `primer-curso` + `sin-fallos`; `award_badges_on_pass` idempotent via `EmployeeBadge` unique_together |
| Runtime harness | `migrate` applies `0003_seed_badges` → 3 badges present; `award_badges_on_pass` on a 1st-attempt pass yields primer-curso + sin-fallos; all-position pass yields catalogo-completo (verified by logic; position-catalog M2M reconciliation) |
| Rollback boundary | Revert `certificates/services.py` `award_badges_on_pass` (and its call in `reading_gate/services._on_pass`); `0003_seed_badges` optional to keep |

### PR5 — Expediente
| Evidence | Value |
|----------|-------|
| Focused test command | `python manage.py test reading_gate` → `Ran 17 tests ... OK` (includes `ExpedienteAndBadgesTests`: pass writes `Expediente` with status/attempts/score/completed_at; admin filter `?course=&status=passed` → 1, `?status=assigned` → 0) |
| Runtime harness | `python manage.py check` clean; Django test client `GET /api/expediente?course=<id>&status=passed` (admin session) → `{"count":1,...}`; full suite `python manage.py test` → 37 tests OK (no regressions in PR1–PR4 apps) |
| Rollback boundary | Revert `reading_gate/models.py` `Expediente` + `services._write_expediente` + `views.expediente_list` + `urls` route + middleware `ADMIN_PREFIXES`; `migrate reading_gate zero` drops `Expediente` (additive). Existing expediente rows are retained data (retention policy) and harmless if code is reverted |

## Deviations / Design Clarifications (PR5)
- **8.2 reused, not re-implemented**: token consumption invalidation + reuse block were delivered in PR2 (`EmployeeAccessToken.redeem` sets `consumed_at`; a presented-but-consumed token returns "consumed"). Marked complete; no new code.
- **Resend idempotency = single active token**: because only token HASHES are stored (raw secret unrecoverable), `resend_access_token` invalidates any prior unconsumed token (marks `consumed_at`) and issues a fresh one, so exactly ONE active token ever exists. This keeps the single-use invariant rather than re-delivering an unrecoverable secret.
- **Cert + Expediente are admin-only** (added `/api/certificate/`, `/api/expediente/` to `ADMIN_PREFIXES`) to honor role isolation while keeping the spec path shapes; employees cannot print certs or read expedientes via the API at MVP.
- **Badge award wired into the pass path** of `grade_submission` (PR4's deferred "badge evaluation"), called via `_on_pass` with lazy import + try/except so a badge/notification failure can NEVER break the pass result. Completion email is auto-sent on pass (best-effort, console transport).
- **Issuance on assignment** is best-effort: a delivery failure is logged (`logger.warning`) but does NOT block enrollment assignment (defensive try/except in `assign_mandatory_courses`).
- **DNI verbatim on certificate**: `employee.dni` returns the exact stored value via `EncryptedDNIField`; the PDF includes it unformatted and the rendered text was verified verbatim via PyPDF2 extraction. `crypto.py`/`fields.py` were NOT modified (debt preserved).
- **No raw token/DNI in logs/audit**: `NotificationLog` stores only recipient+status+detail; `AuditEvent` payloads (from PR4) reference `enrollment_id` + metadata only. A `certificate-issued` audit event was NOT added (optional; formal audit API is PR6).
- **Email transport not exercised with real creds**: default `console` transport is verified (prints link). `smtp`/`resend` are config-gated and require real credentials/network, so their real delivery is NOT verified here (documented).
- **Real PDF visual not verified**: only programmatic text extraction (PyPDF2) confirms fields; pixel-level layout was not visually inspected.

## Remaining Tasks (PR6)
- Phase 14: Audit Log — formal append-only `AuditEvent` API (reject update/delete), full coverage incl. cert issuance event.
- Phase 15: Verification/QA — pytest unit/integration coverage, Playwright E2E (import→read→test→cert), README/run + EU PaaS deploy notes.

## PR / Delivery Status
- **PR5 branch**: `mvp/pr5-secure-cert-badges-expediente` (created stacked off `mvp/pr4-reading-test`, targeting `main`). [chain strategy: stacked-to-main]
- **Commits**: planned as work-unit commits (created locally; push/PR left to a user with remote access, no force-push/no merge):
  (1) `feat(secure-access)` — notifications app: issuance, configurable transport, Spanish templates, delivery log, resend endpoint;
  (2) `feat(certificate)` — certificates: reportlab PDF + admin endpoint + Certificate model + seed migration;
  (3) `feat(badges)` — badge seed + award logic on pass;
  (4) `feat(expediente)` — Expediente model + admin filter + wire into pass/exhaustion;
  (5) `docs(sdd)` — tasks.md `[x]` + merged apply-progress.
- **Prior branches**: `mvp/pr1-scaffold-models` … `mvp/pr4-reading-test` — still awaiting push + PR by a user with remote access. `gh` CLI not available; branches + commits are local only.
- **Known debt gate**: do NOT archive/productionize until the DNI fixed-nonce crypto debt (`backend/common/crypto.py`) is resolved.

## Status
PR1 (9/9) + PR2 (7/7) + PR3 (12/12) + PR4 (8/8) + PR5 (11/11) tasks complete.
Ready for `sdd-verify` of PR5 scope (or proceed to PR6). Awaiting push + PR creation by a user with remote access.

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

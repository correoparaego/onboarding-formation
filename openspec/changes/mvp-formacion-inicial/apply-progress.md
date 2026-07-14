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

## Remaining Tasks (PR3+)
- Phase 5: Course management CRUD + question bank + catalog lookup
- Phase 6: AI generation (`AdminLLMKey` model + endpoints + PII guard)
- Phase 7: Enrollment assignment (auto-enroll on import; idempotency)
- Phase 8: Secure access issuance/delivery + notifications (email)
- Phase 9: Timed reading gate
- Phase 10: Comprehension test
- Phase 11: Certificate
- Phase 12: Badges
- Phase 13: Expediente & filters
- Phase 14: Audit log API
- Phase 15: Verification/QA

## PR / Delivery Status
- **PR2 branch**: `mvp/pr2-auth-import` created locally, stacked off `mvp/pr1-scaffold-models`.
- **Commits**: 2 work-unit commits (auth; import), plus this SDD-artifact commit.
- **PR opened**: NO — `gh` CLI is not installed and no push was performed (per
  instructions: do NOT force-push, do NOT merge). A user with remote access
  must: `git push -u origin mvp/pr2-auth-import` and open a PR targeting
  `main` (stacked-to-main). Once `mvp/pr1-scaffold-models` merges to `main`,
  PR2's diff shrinks to just PR2 changes.
- **Known debt gate**: do NOT archive/productionize until the DNI fixed-nonce
  crypto debt (`backend/common/crypto.py`) is resolved.

## Status
PR1 (9/9) + PR2 (7/7) tasks complete. Ready for `sdd-verify` of PR2 scope or
proceed to PR3. Awaiting push + PR creation by a user with remote access.

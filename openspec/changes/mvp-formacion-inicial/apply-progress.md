# Apply Progress — mvp-formacion-inicial (PR1)

**Change**: mvp-formacion-inicial
**Mode**: Standard (strict_tdd: false — greenfield, no test runner; a model-level smoke check was run instead)
**Delivered work unit**: PR1 — Scaffold + Models/Migrations (stacked-to-main)
**Branch**: `mvp/pr1-scaffold-models` (targets `main`)
**Date**: 2026-07-14

## Completed Tasks
- [x] 1.1 Init Django project + `courses, employees, reading_gate, certificates, notifications, authentication` apps; PostgreSQL settings (SQLite fallback for local boot).
- [x] 1.2 Scaffold React/Vite SPA (`src/admin/*`, `src/employee/*`, `src/components/PdfReader`, `src/api/*`, `src/i18n`).
- [x] 1.3 Configure CORS (env `FRONTEND_BASE_URL`), DRF JSON API, `react-i18next` Spanish default.
- [x] 1.4 Encrypt-at-rest DNI config (`common/crypto.py`, `common/fields.py`) + retention settings hook (`common/retention.py`, `RETENTION_POLICY`).
- [x] 2.1 `employees.Employee`: dni (verbatim, unique, encrypted at rest), name, position, email, phone.
- [x] 2.2 `courses.Course/Section/QuestionBank/Question` (+ `min_time_divisor`, `section_base`, single-correct validation in `clean()`/`save()`).
- [x] 2.3 `reading_gate.Enrollment/ReadingProgress/AuditEvent` (+ expediente/dedup fields).
- [x] 2.4 `certificates.Badge/EmployeeBadge`.
- [x] 2.5 Generate + review migrations (`makemigrations`/`migrate` applied to local SQLite).

## Files Changed
| File | Action | What Was Done |
|------|--------|---------------|
| `backend/manage.py`, `backend/requirements.txt`, `backend/.gitignore` | Created | Django entrypoint, PR1 deps, ignore rules |
| `backend/mvp_project/{settings,urls,wsgi,asgi}.py`, `__init__.py` | Created | Project config: INSTALLED_APPS (6 apps + DRF + CORS), env-driven DB (Postgres/SQLite), CORS from `FRONTEND_BASE_URL`, DRF JSON, RGPD settings, es-es i18n |
| `backend/common/{crypto,retention,fields}.py`, `__init__.py` | Created | Deterministic DNI envelope encryption, retention policy hook, `EncryptedDNIField` |
| `backend/courses/{__init__,apps,models}.py` + `migrations/` | Created | Position, Course, Section, QuestionBank, Question (+ M2M catalog, single-correct validation) |
| `backend/employees/{__init__,apps,models}.py` + `migrations/` | Created | Employee with verbatim encrypted `dni` |
| `backend/reading_gate/{__init__,apps,models}.py` + `migrations/` | Created | Enrollment, ReadingProgress, AuditEvent (append-only) |
| `backend/certificates/{__init__,apps,models}.py` + `migrations/` | Created | Badge, EmployeeBadge |
| `backend/notifications/`, `backend/authentication/` | Created | App skeletons (models added in later phases) + empty migrations |
| `frontend/package.json`, `vite.config.ts`, `tsconfig*.json`, `index.html`, `.gitignore` | Created | Vite + React + TS scaffold config |
| `frontend/src/main.tsx`, `App.tsx`, `vite-env.d.ts` | Created | SPA entry + router |
| `frontend/src/i18n/{index.ts,es.json}` | Created | react-i18next, Spanish default |
| `frontend/src/api/{client.ts,endpoints.ts}` | Created | Axios client (env `VITE_API_BASE_URL`) + typed surface |
| `frontend/src/components/PdfReader/{index.tsx,index.ts}` | Created | Section-gated PDF reader shell (gating logic in Phase 9) |
| `frontend/src/admin/AdminApp.tsx`, `frontend/src/employee/EmployeeApp.tsx` | Created | Admin/employee route shells |
| `openspec/changes/mvp-formacion-inicial/tasks.md` | Modified | PR1 tasks marked `[x]` |
| `openspec/changes/mvp-formacion-inicial/apply-progress.md` | Created | This artifact |

## Work Unit Evidence (PR1)
| Evidence | Value |
|----------|-------|
| Focused test command | `python manage.py check` → "System check identified no issues (0 silenced)"; `python manage.py makemigrations --check --dry-run` → "No changes detected" |
| Runtime harness | `python manage.py migrate` → all PR1 migrations applied to SQLite (employees/courses/reading_gate/certificates OK); model smoke test: `Employee(dni='12345678Z').save()` → read back logical value `'12345678Z'`, DB column stores ciphertext, `'  Spaced DNI '` preserved verbatim (no trim) |
| Frontend harness | `cd frontend && npm install && npm run build` → tsc + vite build succeeded (dist generated) |
| Rollback boundary | Revert branch `mvp/pr1-scaffold-models` (or drop its migrations + app dirs). No data dependency; DB schema is additive and versioned via Django migrations |

## Deviations / Design Clarifications
- **`Position` model added** (implicit in design's `Course.position_catalog (M2M Position→Course)`). Made explicit so the catalog M2M has a concrete target. `Employee.position` remains a verbatim CharField; reconciliation to `Position` happens in later phases.
- **`ReadingProgress` shape**: modeled one row per `(enrollment, section)` storing `accumulated_time` + `device_id`/`session_id`; `reached_section` kept as a denormalized marker (updated on section completion in Phase 9). Faithful to design field list; gating math lands in Phase 9.
- **Encrypt-at-rest is DETERMINISTIC** (fixed nonce) so DNI uniqueness/dedupe hold. Documented security caveat in `common/crypto.py`: a security review must confirm key management before production. Logical DNI value remains byte-for-byte verbatim (employee-import spec satisfied).
- **`Question` single-correct** enforced via `clean()`/`save()` (validates `correct_index` is a valid option index). Design lists only one correct index, so multi-correct is structurally impossible; validation guards authoring.
- **`notifications`/`authentication`** have no models yet (added Phases 8 / 3); apps registered so the project boots and migration history stays consistent.

## Issues Found
- None blocking. (Note: `urllib3`/`requests` version warning during Django commands is a transitive-dependency warning, harmless.)

## Remaining Tasks (PR2+)
- Phase 3: Authentication (admin session, employee magic-link/code, route isolation)
- Phase 4: Employee import (Excel parse, DNI verbatim validation report, dedupe, idempotent enroll)
- Phase 5: Course management CRUD + question bank + catalog lookup
- Phase 6: AI generation (`AdminLLMKey` model + endpoints + PII guard)
- Phase 7: Enrollment assignment
- Phase 8: Secure access + notifications
- Phase 9: Timed reading gate
- Phase 10: Comprehension test
- Phase 11: Certificate
- Phase 12: Badges
- Phase 13: Expediente & filters
- Phase 14: Audit log API
- Phase 15: Verification/QA

## Status
9/9 PR1 tasks complete. Ready for `sdd-verify` of PR1 scope (or proceed to PR2). Awaiting PR creation (needs push/auth — see result).

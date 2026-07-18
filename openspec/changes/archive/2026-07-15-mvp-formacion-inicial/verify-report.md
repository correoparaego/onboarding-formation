# Verification Report — mvp-formacion-inicial

- **Change**: `mvp-formacion-inicial`
- **Mode**: Standard (strict_tdd: false). Persistence: openspec file.
- **Persistence mode**: openspec (`verify-report.md` written to the change folder)
- **Verification date**: 2026-07-15 (re-verification after W1 security fix)
- **Executor**: `sdd-verify` sub-agent (code inspection + real test/check execution)

## 1. Completeness

| Dimension | Source | Status |
|---|---|---|
| Proposal | `proposal.md` | read |
| Specs | 13 capability deltas | read (all 13) |
| Design | `design.md` | read |
| Tasks | `tasks.md` | read — **all 57 tasks `[x]`** |
| Apply progress | `apply-progress.md` | read (PR1–PR6 + W1 fix in PR7) |
| Implementation | `backend/` Django apps | inspected |

**All tasks complete → full verification (not `blocked`).**

## 2. Build / Test / Coverage Evidence

| Command | Exit | Result |
|---|---|---|
| `python manage.py test` | 0 | **Ran 56 tests in 14.966s — OK** |
| `python -m pytest -q` | 0 | collected via `test*.py` harness; 56 pass (1 warning) |
| `python manage.py check` | 0 | System check identified no issues (0 silenced) |
| `python manage.py makemigrations --check --dry-run` | 0 | No changes detected |

- `test_output_hash` (sha256 of the deterministic test summary `Ran 56 tests ... OK`):
  `259a7f8ed39d778cccbb7efcc86c9d34b9abeb4115f359eb668398bab4de60c5`
  (note: includes the run timing; full captured stdout also contains
  non-deterministic console-email magic tokens, so the summary tail is the
  canonical, reproducible evidence)
- `build_output_hash` (sha256 of `manage.py check` stdout + urllib3 warning):
  `71DA9FF7EDBF97363B2D969309E13EAD522C4C2C733DA502C0BB4E5C2B25757A`
- `makemigrations_output_hash` (sha256 of `makemigrations --check` stdout):
  `AE66B78AD96B70C0A9B474CA4969255A6FB323786FC25CB49CBE503F558EBDCE`
- Frontend `npm run build` (tsc + vite) reported green in apply-progress
  (PR1/PR3/PR6); not re-run in this verification (backend-focused). E2E
  Playwright skipped (no browser in env).

**Test count delta vs prior report:** 50 → **56** (+6 from `employees/tests_crypto.py`, the W1 fix acceptance suite).

## 3. Spec Compliance Matrix (13 capabilities)

| # | Capability | Reqs | Scenarios | Implemented | Covering test | Verdict |
|---|---|---|---|---|---|---|
| 1 | employee-import | 4 | 4 | ✓ verbatim DNI (raw cell → `EncryptedDNIField`), validation report, dedupe by DNI, idempotent | ✓ (import parse/report/dedupe; `tests_crypto` verbatim round-trip + duplicate-via-lookup; cert PDF verbatim) | PASS |
| 2 | course-management | 3 | 3 | ✓ PDF+sections CRUD, question bank, position→catalog M2M | ✓ `courses.tests` (catalog, create, single-correct) | PASS |
| 3 | enrollment-assignment | 2 | 2 | ✓ auto-enroll per position on import, idempotent by DNI+course | ✓ `reading_gate.tests` (2 enrollments; re-import 0) | PASS |
| 4 | secure-access | 3 | 3 | ✓ single-use TTL token (hashes only), delivery, consumption invalidation | ✓ `notifications.tests` + `authentication` redeem | PASS |
| 5 | timed-reading | 4 | 4 | ✓ server-authoritative gate (`min_time = ceil(base/divisor)`), visibility+interaction credit, clamp, cross-device resume (enrollment-keyed `ReadingProgress`) | ✓ `reading_gate.tests` (locked-until-minTime, credit, clamp, all-sections-complete) | PASS |
| 6 | comprehension-test | 5 | 5 | ✓ ≤3 attempts (4th→`failed_exhausted`), sha256-deterministic distinct subset, single-correct enforced, fail resets reading, pass→`passed` | ✓ `reading_gate.tests` (distinct, fail-reset, 4th blocked, withhold `correct_index`) | PASS |
| 7 | authentication | 4 | 4 | ✓ admin password session, employee magic-link/code, mutual route isolation (403), admin logout | ✓ `authentication` middleware + views (PR2) | PASS |
| 8 | ai-generation | 6 | 8 | ✓ BYO key encrypted+never-in-response, OpenAI-compatible client, guided draft (HITL, not persisted), PDF→test draft, PII sanitizer wired into prompts, multi-correct rejected at save | ✓ `ai_generation.tests` (no-leak, sanitizer, draft-not-persisted, multi-correct reject) | PASS |
| 9 | certificate | 3 | 3 | ✓ reportlab PDF (name, DNI verbatim, date, title, evaluation, summary index), one active cert (`OneToOne` + deterministic `core_fields_hash`) | ✓ `certificates.tests` (verbatim DNI via PyPDF2, one-cert hash) | PASS |
| 10 | badges | 4 | 4 | ✓ 3 seeded badges, primer-curso / sin-fallos / catalogo-completo award logic, idempotent | ✓ `certificates.tests` + `reading_gate` ExpedienteAndBadges | PASS |
| 11 | expediente | 3 | 3 | ✓ result storage, admin filter `?course=&status=`, retention hook (no delete code) | ✓ `reading_gate.tests` (pass writes expediente; filter) | PASS |
| 12 | audit-log | 4 | 4 | ✓ append-only (create/update/delete rejected 405; read-only admin), no DNI/PII in payloads, device/session context, full coverage events | ✓ `tests_audit` (405, filters, no DNI, coverage) | PASS |
| 13 | notifications | 3 | 3 | ✓ configurable transport (console/smtp/resend), Spanish templates, `NotificationLog` (no token/secret) | ✓ `notifications.tests` (transport, log-no-secret, idempotent resend) | PASS |

**All 13 capabilities compliant with passing covering tests. No regression introduced by the W1 crypto change** (the fix only swaps the DNI-at-rest envelope; all spec-facing behaviors are preserved and the suite is green at 56).

## 4. Correctness Checks (spec-critical behaviors)

| Behavior | Finding | Verdict |
|---|---|---|
| DNI stored VERBATIM (no trim/normalize) | `employees/models.py` passes raw cell string; `EncryptedDNIField.from_db_value` = `decrypt_value` returns exact bytes. Proven by cert PDF assertion (`12345678Z` verbatim) AND `tests_crypto.test_dni_roundtrip_verbatim` (incl. `"  Spaced DNI 12345678z "`). | PASS |
| Dedupe by DNI (post-fix) | Now enforced by `dni_lookup = HashedDNILookupField(unique=True)` (deterministic HMAC `dni_lookup_hash`), NOT by a deterministic ciphertext. `tests_crypto.test_duplicate_dni_rejected_via_lookup` (model) + `test_import_rejects_duplicate_dni` (end-to-end) assert duplicate → rejected, 1 created, 1 duplicate. | PASS |
| Fresh random nonce per encryption | `crypto.encrypt_value` uses `os.urandom(_NONCE_LEN)`; nonce prepended to ciphertext; two encryptions of identical plaintext differ. `tests_crypto.test_fixed_nonce_gone` asserts `hasattr(crypto,'_FIXED_NONCE') is False` and distinct ciphertexts. | PASS |
| Encryption-at-rest preserved | `EncryptedDNIField` still encrypts at rest (random-nonce AES-GCM); `decrypt_value` recovers verbatim. `test_legacy_ciphertext_recoverable` confirms back-compat re-encryption of pre-fix rows. | PASS |
| Timed gate SERVER-authoritative | `process_heartbeat` computes unlock from persisted `ReadingProgress`; client delta clamped to 120s; only visibility+interaction credit. | PASS |
| Cross-device resume | `ReadingProgress` keyed by (enrollment, section) in DB; persisted across devices. | PASS (by design) |
| ≤3 attempts + distinct subset | `get_test_subset` seeded by `sha256(enrollment_id, attempt_no)`; 4th → 409 + `failed_exhausted`. Tests confirm distinct + blocked. | PASS |
| Fail restarts reading | On fail: `ReadingProgress` rows deleted, status→`in_progress`. Test confirms `reading_reset:true`. | PASS |
| Single correct answer | `Question.correct_index` single int + `full_clean()`; bank-create API rejects lists with len≠1. | PASS |
| BYO key encrypted, never logged/exposed | `AdminLLMKey.encrypted_key`; `ai_key_set` returns no key material; raw key decrypted server-side only. | PASS |
| PII-exclusion sanitizer present + wired + tested | `sanitize_text` (no `employees` import) invoked in `prompts.build_*`. Test asserts DNI/email stripped + no Employee import. | PASS |
| Human-in-the-loop (no silent persistence) | `ai_generate_content/tests` return `persisted:false`; no DB write. | PASS |
| Certificate PDF verbatim DNI + one per enrollment | `generate_certificate_pdf` prints `employee.dni`; `Certificate` is `OneToOne`. Test asserts verbatim + identical hash on regen. | PASS |
| Audit append-only + 405 + no DNI | `audit_list` rejects non-GET (405); admin read-only; payloads = metadata only. | PASS |
| Auth: admin session + employee magic-link + route isolation | `RoleIsolationMiddleware` blocks both directions (403); token stored as hash only. | PASS |

## 5. Design Coherence

- Tenancy: single-tenant as designed (no `tenant_id`). ✓
- Reading gate server-authoritative as designed (RGPD 3). ✓
- Deterministic subset per attempt (not Python `hash()`). ✓
- AI: BYO key + OpenAI-compatible wrapper + HITL + PII guard by construction. ✓
- Cert: reportlab primary, no e-signature (RGPD 2). ✓
- Email: configurable transport, no code change to switch. ✓
- Append-only audit enforced end-to-end (API + admin). ✓
- **W1 fix coherence with design**: the fix replaces the fixed-zero-nonce scheme (which violated AES-GCM nonce-uniqueness) with a fresh-random-nonce envelope while keeping the design's verbatim-DNI + encrypt-at-rest intent. Dedup/uniqueness moved to a separate deterministic HMAC (`dni_lookup`) — consistent with the design's "DNI equality handled without leaking the DNI" goal. No design decision contradicted.
- **Deviations** (documented in `apply-progress.md`, non-breaking): `minTime` uses `ceil`; `min_time_divisor=3` default; pass threshold = 100% (`TEST_PASS_THRESHOLD=1.0`, product decision, tunable); subset size = 5; `GET /api/test/questions` added (withholds `correct_index`); PyPDF2 used instead of pdfplumber; real OpenAI client code-reviewed only (fake in tests); E2E opt-in skip.

## 6. Issues

### RESOLVED (previously BLOCKING)
- **W1 — DNI fixed-nonce crypto (AES-GCM nonce reuse) — RESOLVED.** The insecure scheme (`backend/common/crypto.py` previously used a FIXED zero nonce) has been replaced in `employees` `tests_crypto.py` + the W1 fix (PR7 `mvp/fix-w1-dni-crypto`):
  - `encrypt_value` now uses a **fresh random 12-byte nonce per encryption** (`os.urandom`), prepended to the ciphertext; `decrypt_value` recovers it.
  - Dedupe/uniqueness moved to a **deterministic HMAC** (`dni_lookup_hash` → `HashedDNILookupField.dni_lookup`, `unique=True`), so equal DNIs still collide correctly without a deterministic ciphertext.
  - **DNI still stored VERBATIM on read** (`EncryptedDNIField.from_db_value` = `decrypt_value`); duplicate DNI imports are still rejected (via `dni_lookup`).
  - Acceptance covered by 6 new tests in `employees/tests_crypto.py` (verbatim round-trip, distinct-ciphertext/same-lookup, model-level duplicate rejection, import-level duplicate rejection, `_FIXED_NONCE` removed, legacy-ciphertext recoverable). All pass.
  - This was the only BLOCKING item for `sdd-archive`; it is now closed. **No remaining BLOCKING items.**

### WARNING (non-blocking — informational)
- **W2 — Email transport not verified with a real provider.** Default `EMAIL_TRANSPORT=console` is exercised (prints link). `smtp`/`resend` are config-gated and require live credentials/network; their real delivery is code-reviewed only, not executed.
- **W3 — E2E (Playwright) not executed.** No browser in this environment; spec skips gracefully. Verified by the opt-in design + documented run steps; full E2E remains a manual/CI gap.
- **W4 — Real OpenAI-compatible client not exercised at runtime.** `AI_USE_FAKE_LLM=True` makes all AI tests use `FakeLLMClient`; the real `OpenAICompatibleClient` (urllib to `/chat/completions`) is import-safe and code-reviewed but not run against a live key.

### SUGGESTION (informational)
- **S1 — Dedupe is exact-string / case-sensitive.** `"12345678Z"` and `"12345678z"` are treated as distinct DNI values (different `dni_lookup` hash). This is consistent with the verbatim rule but means a case-variant of the same real DNI would create a duplicate employee. Consider a case-insensitive equivalence check for DNI dedupe if business reality treats them as one identifier.
- **S2 — CSRF is exempted** on `/api/auth/*` and `/api/import` (documented MVP trade-off). Add a proper CSRF token flow when the SPA security wiring lands.
- **S3 — `TEST_PASS_THRESHOLD = 1.0`** (every question correct to pass) is a product decision absent from the spec; it is a single named constant and trivially tunable. Confirm with the product owner.
- **S4 — `expediente_list` returns `employee.dni` to admins.** This is intentional for the admin compliance view (expediente spec) and is NOT an audit-log leak (audit payloads contain no DNI). Noted for clarity.

## 7. Final Verdict

**PASS (archive-ready).**

Implementation matches the proposal, all 13 specs, and the design. All 57 tasks are complete; the Django suite runs green (**56 tests**, `manage.py check` clean, migrations stable). The previously-BLOCKING W1 (DNI fixed-nonce crypto debt) is **RESOLVED** by the W1 fix and covered by passing tests — the verbatim-DNI guarantee and duplicate-DNI rejection are preserved, and encryption-at-rest is now nonce-safe.

**No CRITICAL findings. No BLOCKING items.** Remaining WARNINGS (W2 email transport, W3 E2E, W4 live LLM) and SUGGESTIONS (S1–S4) are informational only and do not block `sdd-archive`.

### Archive gate
**CLEARED.** `mvp-formacion-inicial` is ready for `sdd-archive`.

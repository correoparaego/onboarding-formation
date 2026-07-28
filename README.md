# MVP Formación Inicial

Single-company internal web app for **mandatory employee onboarding/training**:
Excel employee import, admin-authored PDF courses with a server-gated timed
reader, comprehension tests, printable certificates, minimal badges, and a
**cross-device, append-only audit log** for compliance evidence.

- **Backend:** Django (Python) JSON API — EU-region managed PaaS.
- **Frontend:** React + Vite SPA — static EU host.
- **Database:** PostgreSQL (Django ORM); SQLite auto-fallback for local boot.
- **Tenancy:** single-tenant MVP (one company).

> ### ✅ DNI ENCRYPTION — SECURITY FIX APPLIED (W1 RESOLVED)
>
> The DNI field is encrypted at rest by `backend/common/crypto.py` using
> **AES-GCM with a fresh, cryptographically-random 12-byte nonce per
> encryption** (nonce prepended to the ciphertext: `nonce || ciphertext ||
> tag`). This eliminates the earlier **fixed-zero-nonce reuse** weakness — a
> real cryptographic break — that was previously tracked as BLOCKING debt.
>
> - Status: **RESOLVED** in the security-fix PR on branch
>   `mvp/fix-w1-dni-crypto` (stacked off `mvp/pr6-audit-qa`, targeting
>   `main`). The change is now clear for archive / production.
> - Dedupe / uniqueness is now enforced by a **separate deterministic HMAC-SHA256**
>   (`dni_lookup_hash`, stored in `HashedDNILookupField.dni_lookup`,
>   `unique=True`). This keeps the DNI **verbatim** on read AND rejects
>   duplicate DNI imports, without a deterministic ciphertext.
> - Existing rows were re-encrypted in place by the `employees` data migration
>   (`0002_w1_dni_crypto`); no manual re-keying is required.
> - `EncryptedDNIField` returns the **verbatim DNI** on read (verbatim
>   guarantee preserved). The audit log and all API responses never include
>   raw DNI in payloads (they reference `enrollment_id` + metadata only).

---

## Prerequisites

- Python ≥ 3.10
- Node.js ≥ 18 (for the SPA)
- PostgreSQL (EU region) for production; SQLite works locally with no env vars
- `pip`, `npm`

## Backend — run locally

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # Linux/macOS
pip install -r requirements.txt

# No DB env vars -> SQLite is used automatically for local boot.
python manage.py migrate
python manage.py runserver 8000
```

The API will be served at `http://localhost:8000/api/...` and the Django
admin at `http://localhost:8000/admin/`.

### Backend environment variables

| Variable | Purpose | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (set a high-entropy value in prod) | insecure dev key |
| `DEBUG` | Django debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `*` |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_HOST` | PostgreSQL connection (all three required to enable Postgres) | — (SQLite fallback) |
| `POSTGRES_PASSWORD` / `POSTGRES_PORT` | Postgres auth/port | `""` / `5432` |
| `FRONTEND_BASE_URL` | CORS-allowed SPA origin(s), comma-separated | `http://localhost:5173` |
| `DNI_ENCRYPTION_KEY` | Key for DNI envelope encryption at rest (set in prod; see debt note) | derived from `SECRET_KEY` (dev only) |
| `EMAIL_TRANSPORT` | `console` (default, prints), `smtp`, or `resend` | `console` |
| `DEFAULT_FROM_EMAIL` | From address for notifications | `no-reply@formacion.local` |
| `RESEND_API_KEY` | Resend API key (only when `EMAIL_TRANSPORT=resend`) | `""` |
| `EMPLOYEE_TOKEN_TTL_SECONDS` | Magic-link/code single-use TTL | `86400` (24h) |
| `AI_USE_FAKE_LLM` | When `True`, AI generation uses a deterministic fake LLM (tests/CI). Leave `False` in prod. | `False` |
| `GEMINI_API_KEY` | Google Gemini API key for default LLM (course generation). Get free at https://aistudio.google.com/app/apikey | — |
| `GEMINI_MODEL` | Gemini model to use | `gemini-3.6-flash` |
| `S3_STORAGE_BUCKET_NAME` | Private bucket for section PDFs | local filesystem |
| `S3_ENDPOINT_URL` | Optional S3-compatible endpoint (R2, MinIO, etc.) | AWS S3 |
| `S3_REGION_NAME` | Bucket region | `eu-west-1` |
| `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | Private bucket credentials | — |

### AI Generation — LLM Priority

The system uses the following priority for LLM selection:

1. **Admin BYO key** — If the admin has configured their own OpenAI-compatible key via `POST /api/ai/key`, that key is used.
2. **Gemini default** — If `GEMINI_API_KEY` is set in environment, Gemini is used as the default LLM.
3. **Fake LLM** — If `AI_USE_FAKE_LLM=True`, the deterministic fake LLM is used (for tests/CI).

This allows the platform to work out-of-the-box with Gemini (free tier available) while still allowing admins to bring their own keys if they prefer.

For Gemini BYO configuration, use the OpenAI-compatible base URL
`https://generativelanguage.googleapis.com/v1beta/openai/`. Saving the key
validates both the credential and model against the provider's `/models`
endpoint before encrypting it.

### Section PDF storage

Section PDFs are never exposed through `/media/`. In production, configure the
five `S3_*` variables above with a private S3-compatible bucket. The application
validates PDF signatures and a 25 MB size limit, then serves files only through
authenticated API routes. Local development falls back to `backend/media/`.

## Frontend — run locally

```bash
cd frontend
npm install
npm run dev        # Vite dev server (http://localhost:5173)
npm run build      # type-check + production build into dist/
```

The SPA calls the Django JSON API via `FRONTEND_BASE_URL`/CORS. Set the API
base URL in the frontend env (e.g. `.env`: `VITE_API_BASE=http://localhost:8000`).

## Tests

### Backend (two equivalent harnesses)

```bash
cd backend

# Option A — Django test runner (always works):
python manage.py test

# Option B — pytest (requires pytest-django, already added to requirements):
pip install -r requirements.txt
python -m pytest
```

Coverage includes: gate math, deterministic test subsets, DNI verbatim,
PII-exclusion sanitizer, AI fake-LLM flows, expediente/badges, and a full
**integration happy path** (`tests_integration.py`): import → read → test →
certificate → append-only audit trail.

### End-to-end (Playwright, optional / opt-in)

The E2E suite is **off by default** and skips gracefully when not enabled, so
local builds without a browser stay green.

```bash
cd frontend
npm install
npm install -D @playwright/test
npx playwright install chromium
RUN_E2E=1 npx playwright test      # or: npm run test:e2e
```

Spec: `frontend/e2e/import-read-test-cert.spec.ts`. It drives the real SPA +
API through import → timed reading → comprehension test → certificate issuance,
and asserts the append-only audit trail records the issuance. Selectors use
`data-testid` hooks — align them with the actual `src/admin/*` and
`src/employee/*` components when enabling E2E.

## Migrations

```bash
cd backend
python manage.py makemigrations --check --dry-run   # verify no pending model changes
python manage.py migrate
```

All schema changes are versioned. Rollback is per-app:
`python manage.py migrate <app> zero` (additive; audit/expediente rows are
retained per the retention policy and are never purged by app rollback).

## EU PaaS deployment notes

Two independent deploy units:

1. **Django backend** → EU-region Python host (e.g. Render / Railway / Fly.io EU).
   - Set `POSTGRES_*` to the EU PostgreSQL instance, `DEBUG=False`,
     a real `DJANGO_SECRET_KEY`, `FRONTEND_BASE_URL` to the static SPA origin,
     and `DNI_ENCRYPTION_KEY` (see security debt above).
2. **React SPA** → EU static host (e.g. the same provider's static tier / Netlify EU / Vercel EU).
   - Build with `npm run build`; serve `dist/`; point it at the backend API URL.
3. **PostgreSQL** → EU managed instance (same region as the backend for latency).
4. **Email provider** → configure `EMAIL_TRANSPORT` (`smtp` or `resend`) with
   `DEFAULT_FROM_EMAIL` / `RESEND_API_KEY`. Spanish templates are built in.
5. **Per-admin AI key** → admins bring their own OpenAI-compatible key
   (`POST /api/ai/key`); it is encrypted at rest, never exposed to the
   client/employee, and never logged. Billing is the admin's own.

### Compliance / RGPD assumptions (product owner must confirm)

- DNI stored verbatim, encrypted at rest, retention policy applied.
- Certificates are printable PDF (no e-signature) — internal record only.
- Reading-time gating is "reasonable control", not human-presence proof.
- Identity binding = email possession (weak) for MVP.
- AI generation sends only course/PDF content — never employee PII.

## Audit log (compliance artifact)

The `AuditEvent` table is **append-only**:

- No create / update / delete endpoint is exposed. Any non-GET on `/api/audit`
  returns **HTTP 405**.
- `/api/audit` (admin-only) supports read/filter by `enrollment`,
  `employee`, `event_type`, and `date`.
- Django admin registers `AuditEvent` as **read-only** (add/change/delete disabled).
- Events never contain DNI / raw tokens / PII — only `enrollment_id` +
  metadata.

Logged events: `import`, `enrollment_assigned`, `section_unlock`,
`section_complete`, `reading_complete`, `attempt_start`, `attempt_submit`,
`attempt_fail`, `attempt_blocked`, `certificate_issued`.

## Project layout

```
backend/
  courses/ employees/ reading_gate/ certificates/
  notifications/ authentication/ ai_generation/ common/ mvp_project/
frontend/
  src/admin/*  src/employee/*  src/components/PdfReader
  src/api/*  src/i18n  e2e/ (Playwright, opt-in)
openspec/changes/mvp-formacion-inicial/   # SDD artifacts (proposal/spec/design/tasks/apply-progress)
```

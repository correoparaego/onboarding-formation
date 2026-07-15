# MVP Formación Inicial

Single-company internal web app for **mandatory employee onboarding/training**:
Excel employee import, admin-authored PDF courses with a server-gated timed
reader, comprehension tests, printable certificates, minimal badges, and a
**cross-device, append-only audit log** for compliance evidence.

- **Backend:** Django (Python) JSON API — EU-region managed PaaS.
- **Frontend:** React + Vite SPA — static EU host.
- **Database:** PostgreSQL (Django ORM); SQLite auto-fallback for local boot.
- **Tenancy:** single-tenant MVP (one company).

> ### ⚠️ KNOWN SECURITY LIMITATION — DNI ENCRYPTION DEBT (BLOCKING)
>
> The DNI field is encrypted at rest by `backend/common/crypto.py`, but that
> module uses a **FIXED zero nonce** for AES-GCM. Reusing a nonce with the
> same key breaks AES-GCM's security guarantees — this is **insecure** and
> MUST be fixed before this app is deployed to **production** or **archived** as
> done.
>
> - Status: **ACCEPTED / DEFERRED** debt (product owner decision). It is
>   intentionally left as-is so the verbatim-DNI + dedupe unique constraint
>   keeps working during development.
> - What to do before production: replace the fixed zero nonce with a
>   unique, randomly generated nonce per encryption (store the nonce alongside
>   the ciphertext, e.g. `nonce || ciphertext || tag`), or move to a
>   vetted envelope (e.g. `django-fernet-fields` / `cryptography`'s
>   `Fernet`). Do **NOT** modify `crypto.py`/`fields.py` until you are
>   ready to re-encrypt existing values.
> - `EncryptedDNIField` currently returns the **verbatim DNI** on read, which
>   the dedupe unique constraint relies on. The verbatim guarantee must be
>   preserved by any replacement.
> - The audit log and all API responses never include raw DNI in payloads
>   (they reference `enrollment_id` + metadata only).

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

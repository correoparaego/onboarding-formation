"""Django settings for the MVP Formación Inicial project.

Single-tenant MVP. PostgreSQL is the production target (EU-region managed PaaS);
SQLite is used automatically when no PostgreSQL env vars are present so the
project can boot and migrations can be generated/verified locally.
"""
from pathlib import Path

import os

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_SECRET_KEY = "dev-insecure-key-change-me-in-production-0123456789"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", DEFAULT_SECRET_KEY)

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")

if not DEBUG and SECRET_KEY == DEFAULT_SECRET_KEY:
    raise ValueError(
        "DJANGO_SECRET_KEY must be set in production (DEBUG=False). "
        "Generate one with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

_default_allowed_hosts = "localhost,127.0.0.1,testserver" if DEBUG else ""
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", _default_allowed_hosts).split(",")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    # Local apps (Phase 1 scaffold)
    "courses",
    "employees",
    "reading_gate",
    "certificates",
    "notifications",
    "authentication",
    "ai_generation",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "authentication.middleware.RoleIsolationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mvp_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mvp_project.wsgi.application"
ASGI_APPLICATION = "mvp_project.asgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# PostgreSQL when env vars are present, otherwise SQLite for local verification.
if all(os.environ.get(k) for k in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_HOST")):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ["POSTGRES_USER"],
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# CORS (env-configured frontend base URL) — task 1.3
# ---------------------------------------------------------------------------
# FRONTEND_BASE_URL may be a comma-separated list of allowed origins.
_frontend_origins = os.environ.get("FRONTEND_BASE_URL", "http://localhost:5173")
CORS_ALLOWED_ORIGINS = [o.strip() for o in _frontend_origins.split(",") if o.strip()]
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# DRF JSON API — task 1.3
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    # Permissions are tightened per-endpoint in later phases (auth, secure-access).
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# ---------------------------------------------------------------------------
# RGPD / encrypt-at-rest DNI + retention — task 1.4
# ---------------------------------------------------------------------------
# Key used for DNI envelope encryption at rest. In production this MUST be set
# via environment (a high-entropy secret). When unset, it is derived from
# SECRET_KEY so the app can boot locally — NEVER rely on the derived key in prod.
DNI_ENCRYPTION_KEY = os.environ.get("DNI_ENCRYPTION_KEY")

# Retention policy (days). audit_days=None means retain indefinitely (compliance).
RETENTION_POLICY = {
    "employee_record_days": int(os.environ.get("RETENTION_EMPLOYEE_DAYS", 365 * 5)),
    "certificate_days": int(os.environ.get("RETENTION_CERT_DAYS", 365 * 5)),
    "audit_days": None,
}

# ---------------------------------------------------------------------------
# Employee access token (magic-link/code) — Phase 3 (spec authentication)
# ---------------------------------------------------------------------------
# Single-use token TTL in seconds. Default 24h; overridable per environment.
EMPLOYEE_TOKEN_TTL_SECONDS = int(os.environ.get("EMPLOYEE_TOKEN_TTL_SECONDS", 60 * 60 * 24))

# ---------------------------------------------------------------------------
# Email transport (Phase 8 — spec notifications §Configurable Email Transport)
# ---------------------------------------------------------------------------
# Selects the delivery backend with NO code change required to switch provider:
#   "console" (default, local) -> prints to stdout, no network
#   "smtp"                      -> Django's configured SMTP backend
#   "resend"                    -> Resend API (needs the `resend` package + key)
EMAIL_TRANSPORT = os.environ.get("EMAIL_TRANSPORT", "console")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "no-reply@formacion.local"
)
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")

# ---------------------------------------------------------------------------
# AI generation (BYO LLM key) — Phase 6 (spec ai-generation)
# ---------------------------------------------------------------------------
# When True, generation endpoints use the deterministic FakeLLMClient so tests
# NEVER call a real provider. Production MUST leave this False.
AI_USE_FAKE_LLM = os.environ.get("AI_USE_FAKE_LLM", "true").lower() in (
    "1",
    "true",
    "yes",
)

# Gemini API key for default LLM (used when admin hasn't configured their own key)
# Get your free API key at: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# ---------------------------------------------------------------------------
# Internationalisation — Spanish default
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static / media
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# WhiteNoise for static files compression and caching
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------------------------
# Production security settings
# ---------------------------------------------------------------------------
if not DEBUG:
    # HTTPS settings (Render provides HTTPS)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True
    SECURE_SSL_REDIRECT = False  # Render handles SSL redirect

    # CSRF trusted origins
    _frontend_url = os.environ.get("FRONTEND_BASE_URL", "")
    if _frontend_url:
        CSRF_TRUSTED_ORIGINS = [_frontend_url]
        if not _frontend_url.startswith("http"):
            CSRF_TRUSTED_ORIGINS = [f"https://{_frontend_url}"]

    # Session and CSRF cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SAMESITE = "None"

    # Additional security
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

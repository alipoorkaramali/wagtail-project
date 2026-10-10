"""
Production settings for Render / Railway / Fly.io deployment.

Reads everything from environment variables so secrets never live in code.
"""
import os

import dj_database_url

from .base import *  # noqa: F403

# ============================================================
#  Core
# ============================================================
DEBUG = False

# SECRET_KEY must be set in env (Render generates one for us)
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY environment variable is not set")  # noqa: F405

# Comma-separated hosts. Example: ".onrender.com,myapp.com,www.myapp.com"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", ".onrender.com,localhost,127.0.0.1").split(",")
    if h.strip()
]

# CSRF trusted origins (required for POST from HTTPS domains)
CSRF_TRUSTED_ORIGINS = [
    f"https://{h.lstrip('.')}" if not h.startswith("http") else h
    for h in ALLOWED_HOSTS
    if h and h != "*"
]
# Also add any extra origins explicitly provided
extra_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if extra_origins:
    CSRF_TRUSTED_ORIGINS += [o.strip() for o in extra_origins.split(",") if o.strip()]

# ============================================================
#  Database
# ============================================================
# Render provides DATABASE_URL. Locally we fall back to SQLite.
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
# else: base.py's SQLite config is used

# ============================================================
#  Static files (WhiteNoise for serving without S3)
# ============================================================
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
}

# ============================================================
#  Security (only enable HTTPS stuff when actually on HTTPS)
# ============================================================
if os.environ.get("RENDER", "") == "true" or os.environ.get("SECURE_SSL_REDIRECT", "") == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"

# ============================================================
#  Logging (so we can see errors in Render's log viewer)
# ============================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ============================================================
#  Local overrides (never used in production, kept for parity)
# ============================================================
try:
    from .local import *  # noqa: F403, F401
except ImportError:
    pass

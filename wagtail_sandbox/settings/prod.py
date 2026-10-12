"""
Production settings for CodeRed Cloud.

See: https://www.codered.cloud/docs/django/environment/
"""
from .base import *  # noqa: F403

import os

DEBUG = False

ALLOWED_HOSTS = [os.environ["VIRTUAL_HOST"]]

SECRET_KEY = os.environ["RANDOM_SECRET_KEY"]

CSRF_TRUSTED_ORIGINS = [
    f"https://{os.environ['VIRTUAL_HOST']}",
]

WAGTAILADMIN_BASE_URL = f"https://{os.environ['VIRTUAL_HOST']}"
WAGTAILAPI_BASE_URL = f"https://{os.environ['VIRTUAL_HOST']}"

VIRTUAL_HOST = os.environ["VIRTUAL_HOST"]

# MCP: token from CodeRed env. Bridge calls /mcp/ in-process (RequestFactory).
# Do NOT set MCP_TARGET_URL to the public site URL — that deadlocks under SSE.
MCP_TOKEN = os.environ.get("MCP_TOKEN", "")
MCP_PUBLIC_URL = os.environ.get(
    "MCP_PUBLIC_URL",
    f"https://{os.environ['VIRTUAL_HOST']}",
)
# Leave empty unless you run a separate MCP process; bridge uses RequestFactory.
MCP_TARGET_URL = os.environ.get("MCP_TARGET_URL", "")

EMAIL_BACKEND = "cr_sendmail.backends.SendmailBackend"

_db_engine = os.environ.get("DB_ENGINE", "django.db.backends.mysql")

if _db_engine.endswith("postgresql") or _db_engine.endswith("postgresql_psycopg2"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.environ["DB_HOST"],
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "OPTIONS": {
                "client_encoding": "UTF8",
                "sslmode": "require",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": os.environ["DB_HOST"],
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "OPTIONS": {
                "charset": "utf8mb4",
                "ssl": {"ssl_mode": "REQUIRED"},
            },
        }
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "/log/django.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
    },
}

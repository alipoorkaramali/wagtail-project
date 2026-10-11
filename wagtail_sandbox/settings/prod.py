"""
Production settings for CodeRed Cloud.

See: https://www.codered.cloud/docs/django/environment/
"""
from .base import *  # noqa: F403

import os

# -- Recommended CodeRed Cloud settings ---------------------------------------

DEBUG = False

ALLOWED_HOSTS = [os.environ["VIRTUAL_HOST"]]

SECRET_KEY = os.environ["RANDOM_SECRET_KEY"]

# CSRF for the public domain
CSRF_TRUSTED_ORIGINS = [
    f"https://{os.environ['VIRTUAL_HOST']}",
]

# Built-in email sending service provided by CodeRed Cloud.
EMAIL_BACKEND = "cr_sendmail.backends.SendmailBackend"

# MySQL (default on CodeRed). Requires SSL + utf8mb4.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": os.environ["DB_HOST"],
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "OPTIONS": {
            "ssl": {},
            "charset": "utf8mb4",
        },
    }
}

# CodeRed serves static/media itself; keep standard paths from base.py.
# Do NOT force WhiteNoise here — CodeRed wires its own static server.

# Logging to CodeRed's /log directory (visible via SFTP)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "/log/django.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["file"],
        },
    },
}

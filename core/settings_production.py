"""
Production settings for the finanpy project.

This module imports all base settings from core.settings and overrides
or extends them with production-specific configuration.

Usage:
    Set the DJANGO_SETTINGS_MODULE environment variable to use this file:
        export DJANGO_SETTINGS_MODULE=core.settings_production

    Or pass it directly to management commands:
        python manage.py migrate --settings=core.settings_production

    For gunicorn:
        gunicorn core.wsgi:application --env DJANGO_SETTINGS_MODULE=core.settings_production
"""

import os

from core.settings import *  # noqa: F401, F403

try:
    import dj_database_url
    _DJ_DATABASE_URL_AVAILABLE = True
except ImportError:
    _DJ_DATABASE_URL_AVAILABLE = False

# ---------------------------------------------------------------------------
# Core overrides
# ---------------------------------------------------------------------------

DEBUG = False

# Enforce SECRET_KEY in production (base settings already raises ValueError,
# but we re-assert here for clarity and to ensure no dev fallback slips through).
_secret_key = os.getenv('SECRET_KEY', '')
if not _secret_key:
    raise ValueError('SECRET_KEY environment variable is required in production.')
SECRET_KEY = _secret_key

# ---------------------------------------------------------------------------
# Middleware - insert WhiteNoise right after SecurityMiddleware
# ---------------------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------------------------------------------------------
# Static files - WhiteNoise configuration
# ---------------------------------------------------------------------------

STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ---------------------------------------------------------------------------
# Database - PostgreSQL via DATABASE_URL environment variable
# ---------------------------------------------------------------------------

_database_url = os.getenv('DATABASE_URL', '')
if _database_url:
    if not _DJ_DATABASE_URL_AVAILABLE:
        raise ImportError(
            'dj-database-url is required when DATABASE_URL is set. '
            'Install it with: pip install dj-database-url'
        )
    DATABASES = {
        'default': dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
# If DATABASE_URL is not set, DATABASES falls back to the SQLite default
# inherited from base settings (useful for smoke-testing the production
# settings locally without a PostgreSQL instance).

# ---------------------------------------------------------------------------
# Email configuration
# ---------------------------------------------------------------------------

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
SERVER_EMAIL = os.getenv('SERVER_EMAIL', EMAIL_HOST_USER)

# ---------------------------------------------------------------------------
# Admins - receives error emails when DEBUG=False
# Format in the environment variable: "Name 1:email1@example.com,Name 2:email2@example.com"
# ---------------------------------------------------------------------------

_admins_raw = os.getenv('ADMINS', '')
if _admins_raw:
    ADMINS = []
    for entry in _admins_raw.split(','):
        entry = entry.strip()
        if ':' in entry:
            name, email = entry.split(':', 1)
            ADMINS.append((name.strip(), email.strip()))

# ---------------------------------------------------------------------------
# Security - all production hardening (base settings already sets these when
# DEBUG=False, but we make them explicit here for documentation clarity).
# ---------------------------------------------------------------------------

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------------------------------------------------------------------------
# Logging - production-level thresholds (WARNING and above to console,
# ERROR and above to file, so INFO-level noise is suppressed).
# ---------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {module}.{funcName}:{lineno} - {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{asctime}] {levelname} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'WARNING',
        },
        'file_error': {
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'errors.log',  # noqa: F405
            'formatter': 'verbose',
            'level': 'ERROR',
        },
        'file_general': {
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'general.log',  # noqa: F405
            'formatter': 'verbose',
            'level': 'WARNING',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_error'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file_error'],
            'level': 'ERROR',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file_general', 'file_error'],
            'level': 'WARNING',
            'propagate': False,
        },
        'transactions': {
            'handlers': ['console', 'file_general', 'file_error'],
            'level': 'WARNING',
            'propagate': False,
        },
        'categories': {
            'handlers': ['console', 'file_general', 'file_error'],
            'level': 'WARNING',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file_general', 'file_error'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

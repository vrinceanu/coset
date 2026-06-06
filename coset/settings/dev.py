from .base import *

print("Using development settings")

DEBUG = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# WAGTAILADMIN_BASE_URL required for notification emails
WAGTAILADMIN_BASE_URL = "http://localhost:8000"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ['django_browser_reload',]
MIDDLEWARE += ['django_browser_reload.middleware.BrowserReloadMiddleware',]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

WAGTAILADMIN_STATIC_FILE_VERSION_STRINGS = False

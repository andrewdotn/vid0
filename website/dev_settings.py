from .common_settings import *
from .util import insert_app_after_django_apps

DEBUG = True

FRONTEND_URL = "http://localhost:3365"

## Database

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "dev.sqlite3",
    }
}

## Debug toolbar

DEBUG_TOOLBAR = True

INSTALLED_APPS = insert_app_after_django_apps(INSTALLED_APPS, "debug_toolbar")

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_COLLAPSED": True,
}

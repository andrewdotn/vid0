from .common_settings import *

DEBUG = False

DEBUG_TOOLBAR = False

# You’ll want to configure this.
ALLOWED_HOSTS = ["website.example.com"]

STATIC_ROOT = BASE_DIR / "public" / "static"

FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "static" / "dist"

FRONTEND_URL = "/static/dist"

STATICFILES_DIRS += [FRONTEND_DIST_DIR.parent]

# Only support https in production. To cover non-django-rendered URLs such as
# public, static, and media files, these need to be configured on the proxy
# webserver as well. In fact, in theory they only need to be configured there.
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 250_000_000  # about six years
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

#

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db" / "prod.sqlite3",
    }
}

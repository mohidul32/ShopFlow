from .base import *  # noqa: F403

if SECRET_KEY == "unsafe-development-secret":  # noqa: F405
    raise RuntimeError("DJANGO_SECRET_KEY must be configured in production.")

if not ALLOWED_HOSTS:  # noqa: F405
    raise RuntimeError("DJANGO_ALLOWED_HOSTS must be configured in production.")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

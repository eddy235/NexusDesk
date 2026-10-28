"""Fail the v1.0 release gate if the synthetic deployment runs insecurely.

Run only with production-like environment variables. This does NOT prove the
public website is secure, and never replaces the live HTTP smoke test.
"""
import os
import sys
from pathlib import Path

# Running this file directly adds scripts/ rather than the project root to sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexusdesk.settings")

from django.conf import settings  # noqa: E402


def validate():
    checks = {
        "debug disabled": settings.DEBUG is False,
        "read-only synthetic demo enabled": settings.DEMO_MODE is True,
        "non-development secret configured": (
            len(settings.SECRET_KEY) >= 32
            and settings.SECRET_KEY != 'dev-only-key-not-for-production-change-me'
        ),
        "explicit allowed hostname": any(
            host not in ('127.0.0.1', 'localhost', '*')
            for host in settings.ALLOWED_HOSTS
        ),
        "HTTPS redirect enabled": settings.SECURE_SSL_REDIRECT is True,
        "session cookie requires HTTPS": settings.SESSION_COOKIE_SECURE is True,
        "CSRF cookie requires HTTPS": settings.CSRF_COOKIE_SECURE is True,
        "HTTP-only session cookie": settings.SESSION_COOKIE_HTTPONLY is True,
        "HSTS explicitly enabled": settings.SECURE_HSTS_SECONDS >= 86400,
        "clickjacking protection": settings.X_FRAME_OPTIONS == 'DENY',
    }
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
    if not all(checks.values()):
        raise SystemExit("Release security configuration failed")


if __name__ == "__main__":
    validate()

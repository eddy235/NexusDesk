"""Strict routing and content policy for the public synthetic showcase."""
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect


_DEMO_CSP = (
    "default-src 'none'; style-src 'self'; img-src 'self'; "
    "script-src 'none'; connect-src 'none'; "
    "form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
)


class DemoGuardMiddleware:
    """The public demo is read-only and never exposes internal application URLs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.DEMO_MODE:
            return self.get_response(request)

        path = request.path
        allowed = path in ('/', '/demo/', '/health/') or path.startswith('/static/')
        if not allowed or request.method not in ('GET', 'HEAD'):
            response = HttpResponseNotFound('Not available in read-only demo mode.')
        elif path == '/':
            response = HttpResponseRedirect('/demo/')
        else:
            response = self.get_response(request)

        response['Content-Security-Policy'] = _DEMO_CSP
        response['Cache-Control'] = 'no-store' if path == '/health/' else 'public, max-age=60'
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return response

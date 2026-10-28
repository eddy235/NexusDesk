from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect


class DemoGuardMiddleware:
    """Allow only synthetic demo pages and static assets in public demo mode."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEMO_MODE:
            path = request.path
            if path == '/' and request.method in ('GET', 'HEAD'):
                return HttpResponseRedirect('/demo/')
            if not (path in ('/', '/demo/', '/health/') or
                    path.startswith('/static/')):
                return HttpResponseNotFound('Not available in read-only demo mode.')
            if request.method not in ('GET', 'HEAD'):
                return HttpResponseNotFound('Read-only demonstration.')
        return self.get_response(request)

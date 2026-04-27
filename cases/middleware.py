from django.conf import settings
from .current_user import set_current_user


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(getattr(request, "user", None))
        return self.get_response(request)


class DynamicCSRFMiddleware:
    """
    Middleware to dynamically add localhost origins to CSRF_TRUSTED_ORIGINS in DEBUG mode.
    This allows any localhost port (e.g., browser preview ports) without manual configuration.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply in DEBUG mode (development)
        if settings.DEBUG:
            origin = request.META.get('HTTP_ORIGIN', '')
            if origin:
                # Check if origin is localhost or 127.0.0.1
                if 'localhost' in origin or '127.0.0.1' in origin:
                    # Add to CSRF_TRUSTED_ORIGINS if not already present
                    if origin not in settings.CSRF_TRUSTED_ORIGINS:
                        settings.CSRF_TRUSTED_ORIGINS.append(origin)
        return self.get_response(request)

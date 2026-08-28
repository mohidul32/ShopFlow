from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def live_health_check(request):
    """A process liveness probe that does not depend on external services."""
    return JsonResponse({"status": "ok"})


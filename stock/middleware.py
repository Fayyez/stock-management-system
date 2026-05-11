import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from stock.exceptions import StockException

logger = logging.getLogger(__name__)


class StockExceptionMiddleware:
    """Handle stock-specific exceptions and provide safe user feedback."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except StockException as exc:
            logger.exception("Stock domain exception: %s", exc)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': str(exc)}, status=400)

            messages.error(request, str(exc))
            return redirect(request.META.get('HTTP_REFERER', '/'))

"""
Secure exception handler and hardened view helpers.
"""

import logging
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('security')


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler.
    - Never leaks stack traces or internal details in production
    - Logs full details server-side
    - Returns generic messages to client
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Log the real error
        request = context.get('request')
        view    = context.get('view')
        logger.warning(
            f"API exception: {type(exc).__name__}: {exc} | "
            f"view={view.__class__.__name__ if view else 'unknown'} | "
            f"path={request.path if request else 'unknown'}"
        )

        # In production, replace detailed errors with generic messages
        if not settings.DEBUG:
            if response.status_code == 400:
                response.data = {'error': 'Invalid request data'}
            elif response.status_code == 401:
                response.data = {'error': 'Authentication required'}
            elif response.status_code == 403:
                response.data = {'error': 'Permission denied'}
            elif response.status_code == 404:
                response.data = {'error': 'Not found'}
            elif response.status_code == 429:
                response.data = {'error': 'Too many requests. Please slow down.'}
            elif response.status_code >= 500:
                response.data = {'error': 'Internal server error'}

    else:
        # Unhandled exception
        logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}", exc_info=True)

        if not settings.DEBUG:
            response = Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return response

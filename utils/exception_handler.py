# utils/exception_handler.py
from rest_framework.views import exception_handler
from .response import error_response
from .friendly_errors import friendly_message


def custom_exception_handler(exc, context):
    drf_response = exception_handler(exc, context)

    if drf_response is not None:
        msg = friendly_message(drf_response.data)
        return error_response(message=msg, status_code=drf_response.status_code)

    # Exceptions DRF didn't handle
    msg = friendly_message(exc)
    return error_response(message=msg, status_code=500)

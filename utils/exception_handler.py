# utils/exception_handler.py
from rest_framework.views import exception_handler
from .response import error_response

def custom_exception_handler(exc, context):
    # Call DRF's default first
    response = exception_handler(exc, context)

    if response is not None:
        # DRF has already generated a response (e.g. ValidationError, 404)
        message = ""
        if isinstance(response.data, dict):
            # Join all error messages into one string
            errors = []
            for field, msgs in response.data.items():
                if isinstance(msgs, (list, tuple)):
                    errors.extend([f"{field}: {m}" for m in msgs])
                else:
                    errors.append(f"{field}: {msgs}")
            message = "; ".join(errors)
        else:
            message = str(response.data)

        return error_response(message=message, status_code=response.status_code)

    # For exceptions DRF didn’t handle
    return error_response(message=str(exc), status_code=500)

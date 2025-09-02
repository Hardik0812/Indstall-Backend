# utils/friendly_errors.py
from collections.abc import Iterable
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import APIException

SIMPLEJWT_CODES = {
    "token_not_valid",
    "token_invalid",
    "token_blacklisted",
    "token_expired",
    "user_inactive",
}


def _extract_simplejwt_message(data: dict) -> str | None:
    code = data.get("code")
    if not code or code not in SIMPLEJWT_CODES:
        return None
    # Prefer messages[].message
    msgs = data.get("messages")
    if isinstance(msgs, Iterable) and not isinstance(msgs, (str, bytes, dict)):
        for item in msgs:
            if isinstance(item, dict) and "message" in item and item["message"]:
                return str(item["message"]).strip()
    # Fallback to detail
    detail = str(data.get("detail", "")).strip()
    if detail:
        return detail
    return "Token not valid"


def _flatten_error_data(data, parent_key=None) -> list[str]:
    # SimpleJWT special case
    if isinstance(data, dict):
        sjwt = _extract_simplejwt_message(data)
        if sjwt:
            return [sjwt]

    out: list[str] = []
    if isinstance(data, dict):
        for field, msgs in data.items():
            no_prefix = field in ("non_field_errors", "detail")
            if isinstance(msgs, dict):
                out.extend(_flatten_error_data(msgs, parent_key=field))
            elif isinstance(msgs, Iterable) and not isinstance(msgs, (str, bytes)):
                for m in msgs:
                    if isinstance(m, (dict, list, tuple)):
                        out.extend(_flatten_error_data(m, parent_key=field))
                    else:
                        out.append(
                            str(m) if no_prefix else f"{_join(field, parent_key)}: {m}"
                        )
            else:
                out.append(
                    str(msgs) if no_prefix else f"{_join(field, parent_key)}: {msgs}"
                )
    elif isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        for item in data:
            out.extend(_flatten_error_data(item, parent_key=parent_key))
    else:
        out.append(str(data))
    return out


def _join(field, parent):
    return f"{parent}.{field}" if parent else field


def friendly_message(err) -> str:
    """
    Accepts:
      - DRF Response .data (dict/list)
      - DRF APIException
      - Django ValidationError
      - Plain Exception
      - dict/list of errors (serializer/form errors, SimpleJWT payloads)
    Returns a short user-facing message.
    """
    # APIException -> detail
    if isinstance(err, APIException):
        data = getattr(err, "detail", None)
        if data:
            msgs = _flatten_error_data(data)
            return msgs[0] if msgs else str(data)

    # Django ValidationError
    if isinstance(err, DjangoValidationError):
        if hasattr(err, "message_dict"):
            msgs = _flatten_error_data(err.message_dict)
            return msgs[0] if msgs else "Invalid input."
        if hasattr(err, "messages"):
            return err.messages[0] if err.messages else "Invalid input."

    # Raw DRF/serializer error data (dict/list)
    if isinstance(err, (dict, list, tuple)):
        msgs = _flatten_error_data(err)
        return msgs[0] if msgs else "Something went wrong."

    # Plain Exception
    text = str(err).strip()
    return text or "Something went wrong."

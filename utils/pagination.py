# common/pagination.py
from __future__ import annotations
from datetime import datetime, date
from typing import Iterable, Tuple, Dict, Any, Optional

from django.core.paginator import Paginator, EmptyPage
from django.utils.dateparse import parse_datetime
from django.utils import timezone


def clamp_int(val: int, lo: int, hi: int) -> int:
    return max(lo, min(val, hi))


def parse_pagination(
    request,
    *,
    default_page: int = 1,
    default_page_size: int = 20,
    max_page_size: int = 100,
) -> Tuple[int, int]:
    """Read ?page= & ?page_size= with safe defaults & caps."""
    try:
        page = int(request.query_params.get("page", default_page))
    except (TypeError, ValueError):
        page = default_page

    try:
        page_size = int(request.query_params.get("page_size", default_page_size))
    except (TypeError, ValueError):
        page_size = default_page_size

    return clamp_int(page, 1, 10_000), clamp_int(page_size, 1, max_page_size)


def parse_iso_dt(s: Optional[str]) -> Optional[datetime]:
    """Accepts ISO datetime or date (YYYY-MM-DD). Returns aware datetime in current TZ."""
    if not s:
        return None
    dt = parse_datetime(s)
    if dt is None:
        # fallback for date-only strings
        try:
            dt = datetime.fromisoformat(s)  # may be date-only
            if isinstance(dt, date) and not isinstance(dt, datetime):
                dt = datetime.combine(dt, datetime.min.time())
        except Exception:
            return None
    # make timezone-aware if naive
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def parse_date_range(
    request, start_key="start", end_key="end"
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Reads ?start=&end= and returns aware datetimes (or None)."""
    return parse_iso_dt(request.query_params.get(start_key)), parse_iso_dt(
        request.query_params.get(end_key)
    )


def validate_ordering(
    request, allowed_fields: Iterable[str], default: str = "-created_at"
) -> str:
    """Validates ?ordering=. Supports field or -field. Falls back to default if invalid."""
    ordering = (request.query_params.get("ordering") or default).strip()
    field = ordering.lstrip("-")
    return ordering if field in set(allowed_fields) else default


def paginate_queryset(qs, page: int, page_size: int) -> Tuple[Any, Dict[str, Any]]:
    """Django Paginator wrapper returning (page_obj, meta)."""
    paginator = Paginator(qs, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages or 1)

    meta = {
        "page": page_obj.number,
        "page_size": page_size,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,
        "has_next": page_obj.has_next(),
        "has_prev": page_obj.has_previous(),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        "prev_page": (
            page_obj.previous_page_number() if page_obj.has_previous() else None
        ),
    }
    return page_obj, meta

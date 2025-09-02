from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from utils.permissions import IsSalesUser
from utils.response import error_response, success_response

from django.db.models import Q
from utils.pagination import (
    parse_pagination,
    validate_ordering,
    paginate_queryset,
    parse_date_range,
)

from .models import QRF


from .serializers import QRFCreateSerializer, QRFDetailSerializer


class QRFCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSalesUser]

    def post(self, request):
        serializer = QRFCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            qrf = serializer.save()
            return success_response(
                message="QRF created successfully.",
                data=QRFDetailSerializer(qrf).data,
                status_code=status.HTTP_201_CREATED,
            )
        return error_response(
            message="Invalid data.",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class QRFListView(APIView):
    """
    GET /api/v1/qrf/
      ?page=1
      &page_size=20
      &search=acme
      &status=DRAFT
      &region=<region_uuid>
      &start=2025-01-01
      &end=2025-12-31
      &ordering=-created_at
    """

    permission_classes = [IsAuthenticated, IsSalesUser]

    # fields clients can order by (prefix '-' allowed)
    ALLOWED_ORDERING = [
        "qrf_no",
        "client_name",
        "consultant_name",
        "job_site",
        "status",
        "created_at",
        "updated_at",
    ]

    def get_queryset(self, request):
        qs = QRF.objects.select_related(
            "sales_region", "sales_engineer", "created_by", "updated_by"
        ).all()

        # --- filters ---
        search = request.query_params.get("search")
        if search:
            s = search.strip()
            qs = qs.filter(
                Q(qrf_no__icontains=s)
                | Q(client_name__icontains=s)
                | Q(consultant_name__icontains=s)
                | Q(job_site__icontains=s)
            )

        status_param = request.query_params.get("status")
        if status_param:
            qs = qs.filter(status__iexact=status_param.strip())

        region_id = request.query_params.get("region")
        if region_id:
            qs = qs.filter(sales_region_id=region_id)

        start_dt, end_dt = parse_date_range(request, start_key="start", end_key="end")
        if start_dt:
            qs = qs.filter(created_at__gte=start_dt)
        if end_dt:
            qs = qs.filter(created_at__lte=end_dt)

        # --- ordering ---
        ordering = validate_ordering(
            request,
            allowed_fields=self.ALLOWED_ORDERING,
            default="-created_at",
        )
        return qs.order_by(ordering)

    def get(self, request):
        qs = self.get_queryset(request)

        # pagination
        page, page_size = parse_pagination(
            request, default_page=1, default_page_size=10, max_page_size=100
        )
        page_obj, meta = paginate_queryset(qs, page=page, page_size=page_size)

        # serialize current page
        serializer = QRFDetailSerializer(page_obj.object_list, many=True)

        payload = {**meta, "results": serializer.data}
        return success_response(
            message="QRFs fetched successfully.",
            data=payload,
            status_code=status.HTTP_200_OK,
        )

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qrf.utils import initialize_qrf_dependencies
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets, status
from utils.response import success_response, error_response
from django.db import IntegrityError

class QRFViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only QRFs created by the logged-in user."""
        return QRF.objects.filter(created_by=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == "list":
            return QRFListSerializer
        return QRFSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(message="QRFs fetched successfully.", data=serializer.data)

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        user = request.user

        try:
            qrf_no = QRF.generate_unique_qrf_no()
        except Exception as e:
            return Response(
                {"success": False, "message": f"Failed to generate QRF number: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = QRFSerializer(data={
            "qrf_no": qrf_no,
            "client_name": payload.get("client_name"),
            "consultant_name": payload.get("consultant_name"),
            "sales_engineer": payload.get("sales_engineer"),
            "sales_region": payload.get("sales_region"),
            "job_site": payload.get("job_site"),
            "design_code": payload.get("design_code"),
            "serviceability_code": payload.get("serviceability_code"),
            "status": "DRAFT",
        })
        serializer.is_valid(raise_exception=True)

        try:
            qrf = serializer.save(created_by=user, updated_by=user)
        except IntegrityError:
            # Retry once in case two requests overlapped
            qrf_no = QRF.generate_unique_qrf_no()
            qrf = serializer.save(created_by=user, updated_by=user, qrf_no=qrf_no)

        # Initialize default dependencies
        initialize_qrf_dependencies(qrf)

        return success_response(
            message="QRF created successfully.",
            data=QRFSerializer(qrf).data,
            status_code=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        """
        Fetch a single QRF with all initialized related tables.
        """
        try:
            qrf = self.get_queryset().get(pk=pk)
        except QRF.DoesNotExist:
            return Response(
                {"success": False, "message": "QRF not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = QRFCompleteSerializer(qrf)
        return success_response(
            message="QRF details fetched successfully.",
            data=serializer.data,
        )

    def partial_update(self, request, pk=None):
        """
        PATCH endpoint — updates all sections of the QRF (nested & base).
        """
        try:
            qrf = self.get_queryset().get(pk=pk)
        except QRF.DoesNotExist:
            return Response(
                {"success": False, "message": "QRF not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = QRFCompleteUpdateSerializer(qrf, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return success_response(
            message="QRF updated successfully.",
            data=serializer.data,
        )
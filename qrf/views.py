from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import IntegrityError, transaction

from utils.response import error_response, success_response
from .models import QRF
from .serializers import QRFSerializer, QRFListSerializer, QRFCompleteSerializer
from .utils import initialize_qrf_dependencies


class QRFCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        payload = request.data
        user = request.user

        # ✅ Safely generate unique QRF number
        try:
            with transaction.atomic():
                qrf_no = QRF.generate_unique_qrf_no()
        except Exception as e:
            return error_response(message="Failed to generate unique QRF number.", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # ✅ Build QRF data
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

        # ✅ Save safely (retry if IntegrityError due to duplicate qrf_no)
        try:
            qrf = serializer.save(created_by=user, updated_by=user)
        except IntegrityError:
            qrf_no = QRF.generate_unique_qrf_no()  # regenerate and retry once
            serializer.validated_data["qrf_no"] = qrf_no
            qrf = serializer.save(created_by=user, updated_by=user)

        # ✅ Initialize all related default dependencies
        initialize_qrf_dependencies(qrf)

        # ✅ Return the newly created record
        return success_response(message="QRF created successfully.", data=QRFSerializer(qrf).data, status_code=status.HTTP_201_CREATED)
  
class QRFListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qrf_list = QRF.objects.filter(created_by=request.user).order_by("-created_at")
        serializer = QRFListSerializer(qrf_list, many=True)
        return success_response(message="QRF list fetched successfully.", data=serializer.data)


class QRFDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            qrf = QRF.objects.get(pk=pk, created_by=request.user)
        except QRF.DoesNotExist:
            return error_response(message="QRF not found.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = QRFCompleteSerializer(qrf)
        return success_response(message="QRF details fetched successfully.", data=serializer.data)


class QRFUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            qrf = QRF.objects.get(pk=pk, created_by=request.user)
        except QRF.DoesNotExist:
            return error_response(message="QRF not found.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = QRFSerializer(qrf, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return success_response(message="QRF updated successfully.", data=serializer.data)


class QRFDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            qrf = QRF.objects.get(pk=pk, created_by=request.user)
            qrf.delete()
        except QRF.DoesNotExist:
            return error_response(message="QRF not found.", status_code=status.HTTP_404_NOT_FOUND)

        return success_response(message="QRF deleted successfully.", data={})

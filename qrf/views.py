import os
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from io import BytesIO
from xhtml2pdf import pisa
from utils.response import error_response, success_response
from .models import QRF
from .serializers import (
    QRFSerializer, 
    QRFListSerializer, 
    QRFCompleteSerializer,
    QRFCompleteUpdateSerializer
)
from .utils import initialize_qrf_dependencies


class QRFCreateView(APIView):
    """
    POST /api/qrf/create/
    
    Creates a new QRF with auto-generated QRF number.
    Optionally accepts nested data for all related tables.
    If no nested data provided, initializes with default templates.
    
    Request body:
    {
        "client_name": "ABC Corp",
        "consultant_name": "XYZ Consultants",
        "sales_engineer": "uuid",
        "sales_region": "uuid",
        "job_site": "Mumbai",
        "design_code": "IS 800",
        "serviceability_code": "IS 875",
        "building_units": [...],  // optional
        "min_thickness_criteria": [...],  // optional
        // ... other nested data
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        payload = request.data.copy()

        try:
            with transaction.atomic():
                # Generate unique QRF number
                qrf_no = QRF.generate_unique_qrf_no()
                payload["qrf_no"] = qrf_no
                payload["status"] = payload.get("status", "DRAFT")

                # Check if nested data is provided
                has_nested_data = any(
                    key in payload for key in [
                        "building_units", "min_thickness_criteria", "secondary_details",
                        "base_conditions", "bracing_conditions", "gravity_loadings",
                        "seismic_loadings", "wind_loadings", "additional",
                        "sheeting_details", "canopies", "framed_openings",
                        "mezzanines", "cranes", "fascias", "partition_walls",
                        "roof_monitors", "louvers", "safety_life_line_systems",
                        "cage_ladders", "pipe_rack_trays"
                    ]
                )

                if has_nested_data:
                    # Create with provided nested data
                    serializer = QRFCompleteUpdateSerializer(data=payload)
                    serializer.is_valid(raise_exception=True)
                    qrf = serializer.save(created_by=user, updated_by=user)
                else:
                    # Create basic QRF and initialize with defaults
                    serializer = QRFSerializer(data=payload)
                    serializer.qrf_no = qrf_no
                    serializer.is_valid(raise_exception=True)
                    qrf = serializer.save(created_by=user, updated_by=user)
                    initialize_qrf_dependencies(qrf)

                # Return complete data
                response_serializer = QRFCompleteSerializer(qrf)
                return success_response(
                    message="QRF created successfully.",
                    data=response_serializer.data,
                    status_code=status.HTTP_201_CREATED
                )

        except IntegrityError as e:
            return error_response(
                message="Failed to create QRF due to data conflict.",
                data={"detail": str(e)},
                status_code=status.HTTP_409_CONFLICT
            )
        except Exception as e:
            return error_response(
                message="Failed to create QRF.",
                data={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

  
class QRFListView(APIView):
    """
    GET /api/qrf/list/
    
    Returns list of all QRFs created by the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qrf_list = QRF.objects.filter(created_by=request.user).order_by("-created_at")
        serializer = QRFListSerializer(qrf_list, many=True)
        return success_response(
            message="QRF list fetched successfully.",
            data=serializer.data
        )


class QRFDetailView(APIView):
    """
    GET /api/qrf/get/<uuid:pk>/
    
    Returns complete QRF details with all nested data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            qrf = QRF.objects.get(pk=pk, created_by=request.user)
        except QRF.DoesNotExist:
            return error_response(
                message="QRF not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = QRFCompleteSerializer(qrf)
        return success_response(
            message="QRF details fetched successfully.",
            data=serializer.data
        )


class QRFUpdateView(APIView):
    """
    PATCH /api/qrf/update/<uuid:pk>/
    
    Updates QRF with complete nested data support.
    Handles create/update/delete of all related records.
    
    Request body can include:
    - QRF header fields (client_name, status, etc.)
    - Any nested arrays (building_units, min_thickness_criteria, etc.)
    
    For nested arrays:
    - Include "id" to update existing records
    - Omit "id" to create new records
    - Records not included in payload will be deleted
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            qrf = QRF.objects.get(pk=pk, created_by=request.user)
        except QRF.DoesNotExist:
            return error_response(
                message="QRF not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
                serializer = QRFCompleteUpdateSerializer(
                    qrf,
                    data=request.data,
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                updated_qrf = serializer.save(updated_by=request.user)

                # Return complete updated data
                response_serializer = QRFCompleteSerializer(updated_qrf)
                return success_response(
                    message="QRF updated successfully.",
                    data=response_serializer.data
                )

        except Exception as e:
            return error_response(
                message="Failed to update QRF.",
                data={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class QRFDeleteView(APIView):
    """
    DELETE /api/qrf/delete/<uuid:pk>/
    
    Soft deletes a QRF (sets deleted_at and deleted_by).
    To permanently delete, use force=true query parameter.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            qrf = QRF.objects.get(pk=pk, created_by=request.user)
        except QRF.DoesNotExist:
            return error_response(
                message="QRF not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        force_delete = request.query_params.get("force", "false").lower() == "true"

        try:
            with transaction.atomic():
                if force_delete:
                    # Permanent delete
                    qrf.delete()
                    message = "QRF permanently deleted successfully."
                else:
                    # Soft delete
                    from django.utils import timezone
                    qrf.deleted_at = timezone.now()
                    qrf.deleted_by = request.user
                    qrf.save(update_fields=["deleted_at", "deleted_by"])
                    message = "QRF deleted successfully."

                return success_response(message=message, data={})

        except Exception as e:
            return error_response(
                message="Failed to delete QRF.",
                data={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return success_response(message="QRF deleted successfully.", data={})


class QRFGeneratePDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):

        # ---------------------------
        # 1️⃣ Fetch QRF
        # ---------------------------
        try:
            qrf = QRF.objects.select_related('sales_engineer', 'sales_region').get(
                pk=pk,
                created_by=request.user
            )
        except QRF.DoesNotExist:
            return error_response(
                message="QRF not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # ---------------------------
        # 2️⃣ Extract related values
        # ---------------------------
        sales_engineer_name = (
            getattr(qrf.sales_engineer, "first_name", None)
            or getattr(qrf.sales_engineer, "full_name", None)
            or getattr(qrf.sales_engineer, "username", None)
            or "N/A"
        )

        sales_region_name = getattr(qrf.sales_region, "name", None) or "N/A"

        # Important: full absolute path for xhtml2pdf
        logo_path = os.path.join(
            settings.BASE_DIR,
            "qrf",
            "static",
            "images",
            "indstaal_logo.png"
        )

        # ---------------------------
        # 3️⃣ Prepare context
        # ---------------------------
        context = {
            "qrf": qrf,
            "sales_engineer_name": sales_engineer_name,
            "sales_region_name": sales_region_name,
            "generated_date": timezone.now().strftime("%B %d, %Y %I:%M %p"),
            "logo_path": logo_path,   # absolute path for PDF images
        }

        # ---------------------------
        # 4️⃣ Render HTML template
        # ---------------------------
        html_string = render_to_string("qrf/pdf_template.html", context)

        # ---------------------------
        # 5️⃣ Convert to PDF (xhtml2pdf)
        # ---------------------------
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=pdf_buffer,
            link_callback=self.link_callback  # handles static & media files
        )

        if pisa_status.err:
            return error_response(
                message="Failed to generate PDF.",
                status_code=500
            )

        pdf_value = pdf_buffer.getvalue()

        # ---------------------------
        # 6️⃣ Return PDF inline
        # ---------------------------
        response = HttpResponse(pdf_value, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="QRF_{qrf.qrf_no}.pdf"'

        return response

    # ------------------------------------------------
    # 🔧 Required for images/static paths in PDF
    # ------------------------------------------------
    def link_callback(self, uri, rel):
        """
        Convert HTML URIs to absolute system paths for xhtml2pdf.
        Handles STATIC and MEDIA files.
        """

        # Static files
        static_root = settings.STATIC_ROOT
        static_url = settings.STATIC_URL

        # Media files
        media_root = settings.MEDIA_ROOT
        media_url = settings.MEDIA_URL

        if uri.startswith(media_url):
            return os.path.join(media_root, uri.replace(media_url, ""))

        elif uri.startswith(static_url):
            return os.path.join(static_root, uri.replace(static_url, ""))

        # Absolute file paths (e.g., logo_path)
        if os.path.isfile(uri):
            return uri

        raise Exception(f"Unable to resolve URI for PDF: {uri}")

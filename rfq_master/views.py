# apps/qrf/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rfq_master.models import Region
from .serializers import RegionSerializer
from utils.response import success_response, error_response


class RegionListAPIView(APIView):
    """
    API endpoint to fetch all active sales regions.
    Returns standardized response using success_response.
    """

    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            regions = (
                Region.objects.filter(is_active=True)
                .only("id", "code", "name")
                .order_by("name")
            )
            serializer = RegionSerializer(regions, many=True)
            return success_response(
                message="Regions fetched successfully.",
                data=serializer.data,
                status_code=200,
            )
        except Exception as e:
            return error_response(
                message="Failed to fetch regions.",
                data={"detail": str(e)},
                status_code=500,
            )
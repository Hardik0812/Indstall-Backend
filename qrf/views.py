from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qrf.utils import initialize_qrf_dependencies
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets, status
from utils.response import success_response, error_response
class QRFViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return only QRFs created by the logged-in user, ordered by creation date.
        """
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

    def perform_create(self, serializer):
        data = serializer.validated_data
        existing = QRF.objects.filter(
            name=data.get("name"), created_by=self.request.user
        ).first()
        if existing:
            return existing

        qrf = serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        initialize_qrf_dependencies(qrf)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class QRFStructuralCriteriaViewSet(viewsets.ModelViewSet):
    """
    Saves all MinThickness, Secondary, Base, and Bracing conditions.
    """
    permission_classes = [IsAuthenticated]
    queryset = (
        QRFMinThicknessCriteria.objects.all()
        .select_related("qrf")
    )
    serializer_class = QRFMinThicknessCriteriaSerializer


class QRFGravityLoadingViewSet(viewsets.ModelViewSet):
    queryset = QRFGravityLoading.objects.all().select_related("qrf")
    serializer_class = QRFGravityLoadingSerializer
    permission_classes = [IsAuthenticated]


class QRFSeismicLoadingViewSet(viewsets.ModelViewSet):
    queryset = QRFSeismicLoading.objects.all().select_related("qrf")
    serializer_class = QRFSeismicLoadingSerializer
    permission_classes = [IsAuthenticated]


class QRFWindLoadingViewSet(viewsets.ModelViewSet):
    queryset = QRFWindLoading.objects.all().select_related("qrf")
    serializer_class = QRFWindLoadingSerializer
    permission_classes = [IsAuthenticated]


class QRFBuildingAdditionViewSet(viewsets.ModelViewSet):
    queryset = QRFBuildingAddition.objects.all().select_related("qrf")
    serializer_class = QRFBuildingAdditionSerializer
    permission_classes = [IsAuthenticated]

class QRFSheetingDetailViewSet(viewsets.ModelViewSet):
    queryset = QRFSheetingDetail.objects.all().select_related("qrf")
    serializer_class = QRFSheetingDetailSerializer
    permission_classes = [IsAuthenticated]

class QRFCanopyViewSet(viewsets.ModelViewSet):
    queryset = QRFCanopy.objects.all().select_related("qrf")
    serializer_class = QRFCanopySerializer
    permission_classes = [IsAuthenticated]


class QRFFramedOpeningViewSet(viewsets.ModelViewSet):
    queryset = QRFFramedOpening.objects.all().select_related("qrf")
    serializer_class = QRFFramedOpeningSerializer
    permission_classes = [IsAuthenticated]


class QRFMezzanineViewSet(viewsets.ModelViewSet):
    queryset = QRFMezzanine.objects.all().select_related("qrf")
    serializer_class = QRFMezzanineSerializer
    permission_classes = [IsAuthenticated]


class QRFCraneViewSet(viewsets.ModelViewSet):
    queryset = QRFCrane.objects.all().select_related("qrf")
    serializer_class = QRFCraneSerializer
    permission_classes = [IsAuthenticated]


class QRFFasciaViewSet(viewsets.ModelViewSet):
    queryset = QRFFascia.objects.all().select_related("qrf")
    serializer_class = QRFFasciaSerializer
    permission_classes = [IsAuthenticated]


class QRFPartitionWallViewSet(viewsets.ModelViewSet):
    queryset = QRFPartitionWall.objects.all().select_related("qrf")
    serializer_class = QRFPartitionWallSerializer
    permission_classes = [IsAuthenticated]


class QRFRoofMonitorViewSet(viewsets.ModelViewSet):
    queryset = QRFRoofMonitor.objects.all().select_related("qrf")
    serializer_class = QRFRoofMonitorSerializer
    permission_classes = [IsAuthenticated]


class QRFLouverViewSet(viewsets.ModelViewSet):
    queryset = QRFLouver.objects.all().select_related("qrf")
    serializer_class = QRFLouverSerializer
    permission_classes = [IsAuthenticated]


class QRFSafetyLifeLineSystemViewSet(viewsets.ModelViewSet):
    queryset = QRFSafetyLifeLineSystem.objects.all().select_related("qrf")
    serializer_class = QRFSafetyLifeLineSystemSerializer
    permission_classes = [IsAuthenticated]


class QRFCageLadderViewSet(viewsets.ModelViewSet):
    queryset = QRFCageLadder.objects.all().select_related("qrf")
    serializer_class = QRFCageLadderSerializer
    permission_classes = [IsAuthenticated]


class QRFPipeRackCableTrayViewSet(viewsets.ModelViewSet):
    queryset = QRFPipeRackCableTray.objects.all().select_related("qrf")
    serializer_class = QRFPipeRackCableTraySerializer
    permission_classes = [IsAuthenticated]

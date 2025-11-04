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



router.register("min-thickness", QRFStructuralCriteriaViewSet, basename="min-thickness")
router.register("gravity-loading", QRFGravityLoadingViewSet, basename="gravity-loading")
router.register("seismic-loading", QRFSeismicLoadingViewSet, basename="seismic-loading")
router.register("wind-loading", QRFWindLoadingViewSet, basename="wind-loading")
router.register("building-additions", QRFBuildingAdditionViewSet, basename="building-additions")
router.register("sheeting", QRFSheetingDetailViewSet, basename="sheeting")
router.register("canopy", QRFCanopyViewSet, basename="canopy")
router.register("framed-opening", QRFFramedOpeningViewSet, basename="framed-opening")
router.register("mezzanine", QRFMezzanineViewSet, basename="mezzanine")
router.register("crane", QRFCraneViewSet, basename="crane")
router.register("fascia", QRFFasciaViewSet, basename="fascia")
router.register("partition-wall", QRFPartitionWallViewSet, basename="partition-wall")
router.register("roof-monitor", QRFRoofMonitorViewSet, basename="roof-monitor")
router.register("louver", QRFLouverViewSet, basename="louver")
router.register("safety-line-system", QRFSafetyLifeLineSystemViewSet, basename="safety-line-system")
router.register("cage-ladder", QRFCageLadderViewSet, basename="cage-ladder")
router.register("pipe-rack-tray", QRFPipeRackCableTrayViewSet, basename="pipe-rack-tray")
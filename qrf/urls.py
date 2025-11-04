from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register("create-qrf", QRFViewSet, basename="qrf")
router.register('list',QRFViewSet, basename="qrf-list")
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

urlpatterns = router.urls

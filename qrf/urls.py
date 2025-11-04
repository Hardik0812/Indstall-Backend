from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register("create", QRFViewSet, basename="qrf")
router.register('list',QRFViewSet, basename="list-qrf")
router.register("get", QRFViewSet, basename="get-qrf")


urlpatterns = router.urls

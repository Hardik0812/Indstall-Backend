from django.urls import path
from .views import RegionListAPIView

urlpatterns = [
    path("list-regions/", RegionListAPIView.as_view(), name="region-list"),
]
from django.urls import path
from .views import QRFCreateView, QRFListView

urlpatterns = [
    path("list/", QRFListView.as_view(), name="qrf_list"),  # GET /api/v1/qrf/
    path("create-qrf/", QRFCreateView.as_view(), name="create_qrf"),
]

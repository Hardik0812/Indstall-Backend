from django.urls import path
from .views import (
    QRFCreateView,
    QRFListView,
    QRFDetailView,
    QRFUpdateView,
    QRFDeleteView,
    QRFGeneratePDFView,
)

urlpatterns = [
    path("create/", QRFCreateView.as_view(), name="qrf-create"),
    path("list/", QRFListView.as_view(), name="qrf-list"),
    path("get/<uuid:pk>/", QRFDetailView.as_view(), name="qrf-get"),
    path("update/<uuid:pk>/", QRFUpdateView.as_view(), name="qrf-update"),
    path("delete/<uuid:pk>/", QRFDeleteView.as_view(), name="qrf-delete"),
    path("generate-pdf/<uuid:pk>/", QRFGeneratePDFView.as_view(), name="qrf-generate-pdf"),
]

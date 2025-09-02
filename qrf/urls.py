from django.urls import path
from .views import QRFCreateView


urlpatterns = [
    path(f"create-qrf/", QRFCreateView.as_view(), name="create_qrf"),
]

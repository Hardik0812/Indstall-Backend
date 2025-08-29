import os
from dotenv import load_dotenv
from django.urls import path
from .views import QRFCreateView
load_dotenv()

ROUTE_PREFIX = os.getenv("ROUTE_PREFIX")

urlpatterns = [
    path(f"{ROUTE_PREFIX}create-qrf/", QRFCreateView.as_view(), name="create_qrf"),
]

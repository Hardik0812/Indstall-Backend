from rest_framework import generics
from rfq_master.models import Region
from .serializers import RegionSerializer

class RegionListAPIView(generics.ListAPIView):
    queryset = Region.objects.filter(is_active=True).order_by("name")
    serializer_class = RegionSerializer

# apps/qrf/serializers.py
from rest_framework import serializers
from rfq_master.models import Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "code", "name", "is_active"]

# apps/qrf/serializers.py
from django.db import transaction
from rest_framework import serializers
from .models import QRF
from rfq_master.models import Region

class QRFCreateSerializer(serializers.ModelSerializer):
    # Accept region by id
    sales_region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.filter(is_active=True))

    class Meta:
        model = QRF
        # status is managed by server; qrf_no/created_* are read-only
        fields = [
            "id", "qrf_no", "revision", "revision_date",
            "client_name", "consultant_name",
            "sales_region", "job_site",
            "status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "qrf_no", "revision", "revision_date", "status", "created_at", "updated_at"]

    def validate(self, attrs):
        # If you want extra validation (e.g., client_name non-empty already ensured by model)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Auto-set:
          - created_by, updated_by = request.user
          - sales_engineer = request.user
          - status = 'DRAFT'
        """
        request = self.context["request"]
        user = request.user

        qrf = QRF.objects.create(
            **validated_data,
            status="DRAFT",
            created_by=user,
            updated_by=user,
            sales_engineer=user,
        )
        # qrf_no is generated in model.save()
        return qrf


class QRFDetailSerializer(serializers.ModelSerializer):
    # For GET responses (if you later add retrieve/list), show region nicely
    sales_region = serializers.SerializerMethodField()
    sales_engineer = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = QRF
        fields = [
            "id", "qrf_no", "revision", "revision_date",
            "client_name", "consultant_name",
            "sales_region", "job_site",
            "status",
            "sales_engineer", "created_by", "updated_by",
            "created_at", "updated_at",
        ]

    def get_sales_region(self, obj):
        return {"id": obj.sales_region.id, "code": obj.sales_region.code, "name": obj.sales_region.name}

    def get_sales_engineer(self, obj):
        return {"id": obj.sales_engineer_id, "email": getattr(obj.sales_engineer, "email", None)}

    def get_created_by(self, obj):
        return {"id": obj.created_by_id, "email": getattr(obj.created_by, "email", None)}

    def get_updated_by(self, obj):
        if not obj.updated_by_id:
            return None
        return {"id": obj.updated_by_id, "email": getattr(obj.updated_by, "email", None)}

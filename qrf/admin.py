# apps/qrf/admin.py
from django.contrib import admin
from .models import QRF
@admin.register(QRF)
class QRFAdmin(admin.ModelAdmin):
    list_display = ("qrf_no", "client_name", "sales_engineer", "status", "revision", "created_at")
    search_fields = ("qrf_no", "client_name", "consultant_name", "job_site")
    list_filter = ("status", "sales_region")
    autocomplete_fields = ("sales_engineer", "created_by", "updated_by")


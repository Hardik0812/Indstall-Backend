from django.db import models
from django.utils import timezone
from django.conf import settings

class BaseModel(models.Model):
    
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="qrf_created_by",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="qrf_updated_by",
        null=True,
        blank=True,
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="qrf_deleted_by",
        null=True,
        blank=True,
    )
    
    class Meta:
        abstract = True

    
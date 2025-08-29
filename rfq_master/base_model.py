import uuid

from django.db import models


class ChoiceBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name

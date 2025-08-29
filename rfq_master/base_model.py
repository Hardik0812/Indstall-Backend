from django.db import models

class ChoiceBase(models.Model):
    code = models.CharField(max_length=50, unique=True)   # e.g., 'NORTH'
    name = models.CharField(max_length=100)              # e.g., '  '
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name
    
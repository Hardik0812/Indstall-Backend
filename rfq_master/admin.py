from django.contrib import admin
from .models import Region, FrameType, SteelGrade, SheetingType, InsulationType, OpeningType, VentType, CraneType
# Register your models here.

admin.site.register(Region)
admin.site.register(FrameType)
admin.site.register(SteelGrade)
admin.site.register(SheetingType)
admin.site.register(InsulationType)     
admin.site.register(OpeningType)
admin.site.register(VentType)
admin.site.register(CraneType)
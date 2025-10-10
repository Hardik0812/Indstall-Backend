from django.contrib import admin
from .models import (
    QRF,
    QRFBuildingUnit,
    QRFBuildingParameter,
    QRFMinThicknessCriteria,
    QRFSecondaryDetails,
    QRFBaseCondition,
    QRFBracingCondition,
    QRFSeismicLoading,
    QRFWindLoading,
    QRFGravityLoading,
    QRFBuildingAddition,
    QRFSheetingDetail,
    QRFCanopy,
    QRFFramedOpening,
    QRFMezzanine,
    QRFCrane,
    QRFFascia,
    QRFPartitionWall,
    QRFRoofMonitor,
    QRFLouver,
    QRFSafetyLifeLineSystem,
    QRFCageLadder,
    QRFPipeRackCableTray,
)

# ---------------------------------------------------------
# Inline Admins (for nested editing inside QRF)
# ---------------------------------------------------------

class QRFBuildingUnitInline(admin.TabularInline):
    model = QRFBuildingUnit
    extra = 0


class QRFBuildingParameterInline(admin.TabularInline):
    model = QRFBuildingParameter
    extra = 0


class QRFMinThicknessInline(admin.TabularInline):
    model = QRFMinThicknessCriteria
    extra = 0


class QRFSecondaryDetailsInline(admin.TabularInline):
    model = QRFSecondaryDetails
    extra = 0


class QRFBaseConditionInline(admin.TabularInline):
    model = QRFBaseCondition
    extra = 0


class QRFBracingConditionInline(admin.TabularInline):
    model = QRFBracingCondition
    extra = 0


class QRFSheetingDetailInline(admin.TabularInline):
    model = QRFSheetingDetail
    extra = 0


class QRFCanopyInline(admin.TabularInline):
    model = QRFCanopy
    extra = 0


class QRFFramedOpeningInline(admin.TabularInline):
    model = QRFFramedOpening
    extra = 0


class QRFMezzanineInline(admin.TabularInline):
    model = QRFMezzanine
    extra = 0


class QRFCraneInline(admin.TabularInline):
    model = QRFCrane
    extra = 0


class QRFFasciaInline(admin.TabularInline):
    model = QRFFascia
    extra = 0


class QRFPartitionWallInline(admin.TabularInline):
    model = QRFPartitionWall
    extra = 0


class QRFRoofMonitorInline(admin.TabularInline):
    model = QRFRoofMonitor
    extra = 0


class QRFLouverInline(admin.TabularInline):
    model = QRFLouver
    extra = 0


class QRFSafetyLifeLineSystemInline(admin.TabularInline):
    model = QRFSafetyLifeLineSystem
    extra = 0


class QRFCageLadderInline(admin.TabularInline):
    model = QRFCageLadder
    extra = 0


class QRFPipeRackCableTrayInline(admin.TabularInline):
    model = QRFPipeRackCableTray
    extra = 0


class QRFBuildingAdditionInline(admin.TabularInline):
    model = QRFBuildingAddition
    extra = 0


class QRFGravityLoadingInline(admin.TabularInline):
    model = QRFGravityLoading
    extra = 0


class QRFSeismicLoadingInline(admin.TabularInline):
    model = QRFSeismicLoading
    extra = 0


class QRFWindLoadingInline(admin.TabularInline):
    model = QRFWindLoading
    extra = 0


# ---------------------------------------------------------
# QRF Main Admin — Master Inline Structure
# ---------------------------------------------------------


@admin.register(QRF)
class QRFAdmin(admin.ModelAdmin):
    list_display = ("qrf_no", "client_name", "sales_engineer", "status", "created_at")
    list_filter = ("status", "sales_region", "created_at")
    search_fields = ("qrf_no", "client_name", "consultant_name", "job_site")
    readonly_fields = ("qrf_no", "created_at", "updated_at")

    inlines = [
        QRFBuildingUnitInline,
        QRFMinThicknessInline,
        QRFSecondaryDetailsInline,
        QRFBaseConditionInline,
        QRFBracingConditionInline,
        QRFSeismicLoadingInline,
        QRFWindLoadingInline,
        QRFGravityLoadingInline,
        QRFBuildingAdditionInline,
        QRFSheetingDetailInline,
        QRFCanopyInline,
        QRFFramedOpeningInline,
        QRFMezzanineInline,
        QRFCraneInline,
        QRFFasciaInline,
        QRFPartitionWallInline,
        QRFRoofMonitorInline,
        QRFLouverInline,
        QRFSafetyLifeLineSystemInline,
        QRFCageLadderInline,
        QRFPipeRackCableTrayInline,
    ]

    fieldsets = (
        ("Basic Information", {
            "fields": ("qrf_no", "client_name", "consultant_name", "sales_engineer", "sales_region", "job_site"),
        }),
        ("Status & Revision", {
            "fields": ("status", "revision", "revision_date", "design_code", "serviceability_code"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )


# ---------------------------------------------------------
# Register all child models individually (for standalone access)
# ---------------------------------------------------------

@admin.register(QRFBuildingUnit)
class QRFBuildingUnitAdmin(admin.ModelAdmin):
    list_display = ("qrf", "unit_type", "name", "frame_type")
    list_filter = ("unit_type", "frame_type")
    inlines = [QRFBuildingParameterInline]


@admin.register(QRFBuildingParameter)
class QRFBuildingParameterAdmin(admin.ModelAdmin):
    list_display = ("building_unit", "parameter_type", "dimension_value", "unit", "end_condition")
    list_filter = ("parameter_type",)


admin.site.register(QRFMinThicknessCriteria)
admin.site.register(QRFSecondaryDetails)
admin.site.register(QRFBaseCondition)
admin.site.register(QRFBracingCondition)
admin.site.register(QRFSeismicLoading)
admin.site.register(QRFWindLoading)
admin.site.register(QRFGravityLoading)
admin.site.register(QRFBuildingAddition)
admin.site.register(QRFSheetingDetail)
admin.site.register(QRFCanopy)
admin.site.register(QRFFramedOpening)
admin.site.register(QRFMezzanine)
admin.site.register(QRFCrane)
admin.site.register(QRFFascia)
admin.site.register(QRFPartitionWall)
admin.site.register(QRFRoofMonitor)
admin.site.register(QRFLouver)
admin.site.register(QRFSafetyLifeLineSystem)
admin.site.register(QRFCageLadder)
admin.site.register(QRFPipeRackCableTray)

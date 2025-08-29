# apps/qrf/models.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from rfq_master.models import Region
# ---------- QRF Header ----------

class QRF(models.Model):
    """
    Quote Request Form (header row).
    """
    qrf_no = models.CharField(max_length=50, unique=True, editable=False)
    revision = models.PositiveIntegerField(default=0)
    revision_date = models.DateField(null=True, blank=True)

    client_name = models.CharField(max_length=255)
    consultant_name = models.CharField(max_length=255, blank=True)
    sales_engineer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="qrf_created",
        help_text="User (Sales) who created the QRF"
    )
    sales_region = models.ForeignKey(Region, on_delete=models.PROTECT)
    job_site = models.CharField(max_length=255, blank=True)

    # Admin/audit
    status = models.CharField(max_length=30, default="DRAFT", help_text="DRAFT / SUBMITTED / APPROVED / REJECTED")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="qrf_created_by")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="qrf_updated_by", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="qrf_deleted_by", null=True, blank=True)


    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.qrf_no} (rev {self.revision})"

    def save(self, *args, **kwargs):
        if not self.qrf_no:  # only generate first time
            prefix = "IND"  # or fetch dynamically from settings/region
            year = timezone.now().year
            # Count existing QRFs this year to generate sequence
            last_qrf = QRF.objects.filter(
                created_at__year=year
            ).order_by("-id").first()

            if last_qrf and last_qrf.qrf_no.startswith(f"{prefix}-{year}"):
                # extract last sequence number
                try:
                    last_seq = int(last_qrf.qrf_no.split("-")[-1])
                except ValueError:
                    last_seq = 0
                new_seq = last_seq + 1
            else:
                new_seq = 1

            self.qrf_no = f"{prefix}-{year}-{new_seq:04d}"

        super().save(*args, **kwargs)

# # ---------- Building Parameters ----------

# class QRFBuilding(models.Model):
#     qrf = models.OneToOneField(QRF, on_delete=models.CASCADE, related_name="building")
#     design_code = models.CharField(max_length=100, default="AISC-360-2016", blank=True)
#     frame_type = models.CharField(max_length=30, choices=FrameType.choices, default=FrameType.CLEAR_SPAN)
#     width_m = models.DecimalField(max_digits=8, decimal_places=3, validators=[MinValueValidator(0)])
#     length_m = models.DecimalField(max_digits=8, decimal_places=3, validators=[MinValueValidator(0)])
#     clear_height_m = models.DecimalField(max_digits=6, decimal_places=3, validators=[MinValueValidator(0)])
#     base_plate_below_ffl_mm = models.IntegerField(default=0, help_text="Base plate bottom wrt FFL (mm)")

#     roof_slope_ratio = models.DecimalField(
#         max_digits=5, decimal_places=3, default=0.0, help_text="e.g. 0.5 => 1:2 slope"
#     )

#     # Bay spacing and internal columns can be complex; store structured details as JSON
#     bay_spacing_m = models.JSONField(default=list, blank=True, help_text="List of bay spacings in meters")
#     internal_columns = models.JSONField(default=dict, blank=True, help_text="{'count': int, 'spacing_m': [...]}")

#     # Bracing (roof/wall)
#     roof_bracing = models.CharField(max_length=100, blank=True, help_text="e.g., Full ht. cross bracing @ bays")
#     wall_bracing = models.CharField(max_length=100, blank=True)

#     # Mezzanine summary; detailed per-level captured in QRFMezzanine
#     has_mezzanine = models.BooleanField(default=False)

#     # Drainage
#     gutters_required = models.BooleanField(default=True)
#     downspouts_required = models.BooleanField(default=True)
#     header_pipe_arrangement = models.CharField(max_length=255, blank=True)

#     notes = models.TextField(blank=True)

#     def __str__(self) -> str:
#         return f"Building for {self.qrf.qrf_no}"


# class QRFMezzanine(models.Model):
#     qrf = models.ForeignKey(QRF, on_delete=models.CASCADE, related_name="mezzanines")
#     level_name = models.CharField(max_length=50, default="Mezzanine")
#     area_m2 = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
#     live_load_kN_m2 = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
#     slab_type = models.CharField(max_length=100, blank=True)  # e.g., Deck slab / RCC / etc.
#     remarks = models.CharField(max_length=255, blank=True)


# # ---------- Material / Section Specs ----------

# class QRFMaterialSpec(models.Model):
#     qrf = models.OneToOneField(QRF, on_delete=models.CASCADE, related_name="materials")

#     main_frame_steel = models.CharField(max_length=40, choices=SteelGrade.choices, default=SteelGrade.ASTM_A572GR50)
#     secondary_steel = models.CharField(max_length=40, choices=SteelGrade.choices, default=SteelGrade.ASTM_A36)
#     anchor_bolts = models.CharField(max_length=100, blank=True)  # e.g., ASTM F1554 Gr.55
#     ceb_required = models.BooleanField(default=False, help_text="Column End Base / Expansion bolts")

#     purlin_spacing_m = models.DecimalField(max_digits=5, decimal_places=3, validators=[MinValueValidator(0)], null=True, blank=True)
#     girt_spacing_m = models.DecimalField(max_digits=5, decimal_places=3, validators=[MinValueValidator(0)], null=True, blank=True)

#     frame_design_notes = models.TextField(blank=True)
#     secondary_members_notes = models.TextField(blank=True)


# # ---------- Cladding / Roof & Wall ----------

# class QRFCladdingSpec(models.Model):
#     qrf = models.OneToOneField(QRF, on_delete=models.CASCADE, related_name="cladding")

#     roof_sheet = models.CharField(max_length=40, choices=SheetingType.choices, default=SheetingType.TCT_COLOR_0475)
#     wall_sheet = models.CharField(max_length=40, choices=SheetingType.choices, default=SheetingType.TCT_COLOR_0475)

#     roof_liner = models.CharField(max_length=40, choices=SheetingType.choices, default=SheetingType.OTHER, blank=True)
#     wall_liner = models.CharField(max_length=40, choices=SheetingType.choices, default=SheetingType.OTHER, blank=True)

#     roof_insulation_type = models.CharField(max_length=30, choices=InsulationType.choices, default=InsulationType.NONE)
#     roof_insulation_thickness_mm = models.PositiveIntegerField(null=True, blank=True)

#     wall_insulation_type = models.CharField(max_length=30, choices=InsulationType.choices, default=InsulationType.NONE)
#     wall_insulation_thickness_mm = models.PositiveIntegerField(null=True, blank=True)

#     skylight_percent = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
#     skylight_notes = models.CharField(max_length=255, blank=True)

#     roof_vent_type = models.CharField(max_length=30, choices=VentType.choices, default=VentType.NONE)
#     vent_qty = models.PositiveIntegerField(default=0)

#     color_notes = models.CharField(max_length=255, blank=True)
#     special_panels = models.CharField(max_length=255, blank=True)  # e.g., PU/PIR panels, sandwich, etc.


# # ---------- Openings / Accessories ----------

# class QRFOpening(models.Model):
#     qrf = models.ForeignKey(QRF, on_delete=models.CASCADE, related_name="openings")
#     opening_type = models.CharField(max_length=30, choices=OpeningType.choices, default=OpeningType.OTHER)
#     width_m = models.DecimalField(max_digits=6, decimal_places=3, validators=[MinValueValidator(0)])
#     height_m = models.DecimalField(max_digits=6, decimal_places=3, validators=[MinValueValidator(0)])
#     quantity = models.PositiveIntegerField(default=1)

#     location = models.CharField(max_length=100, blank=True, help_text="e.g., Grid/Bay reference")
#     is_motorized = models.BooleanField(default=False)
#     glazing = models.CharField(max_length=100, blank=True)  # for windows
#     remarks = models.CharField(max_length=255, blank=True)


# class QRFCanopy(models.Model):
#     qrf = models.ForeignKey(QRF, on_delete=models.CASCADE, related_name="canopies")
#     description = models.CharField(max_length=255, help_text="e.g., 3m canopy @ Bay 1-2")
#     projection_m = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
#     length_m = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
#     sheet_type = models.CharField(max_length=40, choices=SheetingType.choices, default=SheetingType.OTHER, blank=True)
#     remarks = models.CharField(max_length=255, blank=True)


# class QRFCrane(models.Model):
#     qrf = models.ForeignKey(QRF, on_delete=models.CASCADE, related_name="cranes")
#     crane_type = models.CharField(max_length=20, choices=CraneType.choices, default=CraneType.EOT)
#     capacity_t = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
#     span_m = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
#     qty = models.PositiveIntegerField(default=1)
#     hook_height_m = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
#     remarks = models.CharField(max_length=255, blank=True)


# # ---------- Files / Revisions / Notes ----------

# def qrf_upload_to(instance: "QRFAttachment", filename: str) -> str:
#     return f"qrf/{instance.qrf.qrf_no}/attachments/{filename}"

# class QRFAttachment(models.Model):
#     qrf = models.ForeignKey(QRF, on_delete=models.CASCADE, related_name="attachments")
#     file = models.FileField(upload_to=qrf_upload_to)
#     description = models.CharField(max_length=255, blank=True)
#     uploaded_at = models.DateTimeField(default=timezone.now)
#     uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

# class QRFRevision(models.Model):
#     qrf = models.ForeignKey(QRF, on_delete=models.CASCADE, related_name="revisions")
#     revision_no = models.PositiveIntegerField()
#     changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
#     changed_at = models.DateTimeField(default=timezone.now)
#     change_notes = models.TextField(blank=True)

#     class Meta:
#         unique_together = [("qrf", "revision_no")]
#         ordering = ["-changed_at"]


# class QRFNote(models.Model):
#     qrf = models.ForeignKey(QRF, on_delete=models.CASCADE, related_name="notes")
#     note = models.TextField()
#     added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
#     added_at = models.DateTimeField(default=timezone.now)

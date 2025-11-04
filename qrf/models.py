# apps/qrf/models.py
from __future__ import annotations
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from rfq_master.models import Region
from utils.base_model import BaseModel
from django.db import transaction
# ---------- QRF Header ----------


class QRF(BaseModel):
    """
    Quote Request Form (header row).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf_no = models.CharField(max_length=50, unique=True, editable=False)
    revision = models.PositiveIntegerField(default=0)
    revision_date = models.DateField(null=True, blank=True)

    client_name = models.CharField(max_length=255)
    consultant_name = models.CharField(max_length=255, blank=True)
    sales_engineer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="qrf_created",
        help_text="User (Sales) who created the QRF",
    )
    sales_region = models.ForeignKey(Region, on_delete=models.PROTECT)
    job_site = models.CharField(max_length=255, blank=True)

    # Admin/audit
    status = models.CharField(
        max_length=30,
        default="DRAFT",
        help_text="DRAFT / SUBMITTED / APPROVED / REJECTED",
    )
    design_code = models.CharField(max_length=50, blank=True)
    serviceability_code = models.CharField(max_length=50, blank=True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.qrf_no} (rev {self.revision})"

    @classmethod
    def generate_unique_qrf_no(cls):
        """
        Generates a unique, sequential QRF number like IND-2025-0004.
        This is done atomically to avoid duplicates under concurrency.
        """
        with transaction.atomic():
            year = timezone.now().year
            prefix = f"IND-{year}-"

            # Lock table rows for this query to avoid race conditions
            last = (
                cls.objects.select_for_update()
                .filter(qrf_no__startswith=prefix)
                .order_by("-created_at")
                .first()
            )

            if last and last.qrf_no:
                try:
                    last_number = int(last.qrf_no.split("-")[-1])
                except Exception:
                    last_number = 0
            else:
                last_number = 0

            next_number = last_number + 1
            return f"{prefix}{next_number:04d}"
        
    # def save(self, *args, **kwargs):
    #     if not self.qrf_no:  # only generate first time
    #         prefix = "IND"  # or fetch dynamically from settings/region
    #         year = timezone.now().year
    #         # Count existing QRFs this year to generate sequence
    #         last_qrf = QRF.objects.filter(created_at__year=year).order_by("-id").first()

    #         if last_qrf and last_qrf.qrf_no.startswith(f"{prefix}-{year}"):
    #             # extract last sequence number
    #             try:
    #                 last_seq = int(last_qrf.qrf_no.split("-")[-1])
    #             except ValueError:
    #                 last_seq = 0
    #             new_seq = last_seq + 1
    #         else:
    #             new_seq = 1

    #         self.qrf_no = f"{prefix}-{year}-{new_seq:04d}"

    #     super().save(*args, **kwargs)



class QRFBuildingUnit(models.Model):
    """
    Represents a single building unit (Main Building or a Lean-To Shed).
    """
    
    UNIT_TYPE_CHOICES = [
        ("MAIN", "Main Building"),
        ("LEAN_TO", "Lean-To Shed"),
    ]

    FRAME_TYPE_CHOICES = [
        ("RF", "RF (Main Building)"),
        ("LEAN_TO", "Lean-To"),
        ("CRANE", "Crane Support"),
        ("CANOPY", "Canopy"),
        ("OPEN", "Open Structure"),
        ("OTHER", "Other"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="building_units")

    unit_type = models.CharField(max_length=10, choices=UNIT_TYPE_CHOICES, default="MAIN")
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional name like Main-1, Lean-To-1, Lean-To Loading Shed"
    )

    frame_type = models.CharField(max_length=30, choices=FRAME_TYPE_CHOICES, blank=True)
    order = models.PositiveIntegerField(default=1, help_text="Used to order lean-tos sequentially")

    def __str__(self):
        return f"{self.get_unit_type_display()} ({self.name or self.id}) for {self.qrf.qrf_no}"

class QRFBuildingParameter(models.Model):
    """
    Represents each parameter row (e.g. Width, Length, Clear Height)
    for a specific building unit.
    """

    END_CONDITION_CHOICES = [
        ("C/C_COL", "C/C of Column"),
        ("O/O_STEEL", "O/O of Steel"),
        ("WITH_CANTILEVER", "With Cantilever"),
        ("WITHOUT_CANTILEVER", "Without Cantilever"),
        ("NA", "Not Applicable"),
    ]

    UNIT_CHOICES = [
        ("meter", "Meter"),
        ("degree", "Degree"),
        ("number", "Number"),
        ("boolean", "Yes/No"),
        ("text", "Text"),
    ]

    PARAMETER_CHOICES = [
        ("WIDTH", "Width (m)"),
        ("LENGTH", "Length (m)"),
        ("CLEAR_HEIGHT", "Clear Height (m)"),
        ("BASE_PLATE", "Base Plate Bottom With ref to FFL"),
        ("ROOF_SLOPE", "Roof Slope"),
        ("BAY_SPACING", "Bay Spacing (C/C)"),
        ("INTERNAL_COLUMN", "Internal Column Nos & Spacing"),
        ("END_WALL_COLUMN", "End Wall Column Spacing"),
        ("BWALL_FRONT", "B/wall Condition : Front Side wall"),
        ("BWALL_BACK", "B/wall Condition : Back Side wall"),
        ("BWALL_LEFT", "B/wall Condition : Left End wall"),
        ("BWALL_RIGHT", "B/wall Condition : Right End wall"),
        ("FUTURE_EXPANSION", "Future Expansion"),
        ("ROOF_EXTENSION", "Roof Extension"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building_unit = models.ForeignKey(QRFBuildingUnit, on_delete=models.CASCADE, related_name="parameters")
    parameter_type = models.CharField(max_length=50, choices=PARAMETER_CHOICES)

    dimension_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    text_value = models.CharField(max_length=255, blank=True)  # For text-based inputs like wall conditions
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, blank=True)
    end_condition = models.CharField(max_length=30, choices=END_CONDITION_CHOICES, blank=True)

    extra_data = models.JSONField(default=dict, blank=True, help_text="Optional data for special cases")

    def __str__(self):
        return f"{self.get_parameter_type_display()} for {self.building_unit}"



class QRFMinThicknessCriteria(models.Model):
    """
    Rows for Min Thickness Criteria section (B/U Web, B/U Flange, etc.).
    Each record can be added from Admin dynamically.
    """
    THICKNESS_CHOICES = [
        ("AS_PER_DESIGN", "As per design"),
        ("6MM", "6 mm"),
        ("8MM", "8 mm"),
        ("10MM", "10 mm"),
        ("12MM", "12 mm"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="min_thickness_criteria")
    name = models.CharField(max_length=100, help_text="Label, e.g. 'B/U Web'")
    dropdown = models.CharField(max_length=50, choices=THICKNESS_CHOICES, blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_dropdown_display()} ({self.qrf.qrf_no})"


class QRFSecondaryDetails(models.Model):
    """
    Rows for Secondary Details section (Purlin spacing, Girt spacing, etc.).
    """
    SPACING_CHOICES = [
        ("AS_PER_DESIGN", "As per design"),
        ("900", "900 mm"),
        ("1000", "1000 mm"),
        ("1200", "1200 mm"),
        ("1500", "1500 mm"),
    ]
    GSM_CHOICES = [
        ("120", "120 GSM"),
        ("180", "180 GSM"),
        ("240", "240 GSM"),
        ("275", "275 GSM"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="secondary_details")
    name = models.CharField(max_length=100, help_text="Label, e.g. 'Purlin spacing'")
    dropdown = models.CharField(max_length=50, choices=SPACING_CHOICES, blank=True)

    def __str__(self):
        return f"{self.name} - {self.dropdown} ({self.qrf.qrf_no})"


class QRFBaseCondition(models.Model):
    """
    Rows for Base Condition section (Main Col bases, CB Col bases, etc.).
    """
    BASE_CHOICES = [
        ("AS_PER_DESIGN", "As per design"),
        ("FIXED", "Fixed"),
        ("PINNED", "Pinned"),
        ("HINGED", "Hinged"),
    ]   
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="base_conditions")
    name = models.CharField(max_length=100, help_text="Label, e.g. 'Main Col bases'")
    dropdown = models.CharField(max_length=50, choices=BASE_CHOICES, blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_dropdown_display()} ({self.qrf.qrf_no})"


class QRFBracingCondition(models.Model):
    """
    Rows for Bracing Condition section (Roof member, Wall member, etc.).
    """
    BRACING_CHOICES = [
        ("AS_PER_DESIGN", "As per design"),
        ("FULL_HT_CROSS", "Full height cross"),
        ("DIAGONAL", "Diagonal"),
        ("K_BRACE", "K-Brace"),
        ("NONE", "None"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="bracing_conditions")
    name = models.CharField(max_length=100, help_text="Label, e.g. 'Roof member'")
    dropdown = models.CharField(max_length=50, choices=BRACING_CHOICES, blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_dropdown_display()} ({self.qrf.qrf_no})"

class QRFSeismicLoading(models.Model):

    BRACING_CHOICES = [
        ("AS_PER_DESIGN", "As per design"),
        ("FULL_HT_CROSS", "Full height cross"),
        ("DIAGONAL", "Diagonal"),
        ("K_BRACE", "K-Brace"),
        ("NONE", "None"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="seismic_loadings")
    name = models.CharField(max_length=100, help_text="Label, e.g. 'Roof member'")
    dropdown = models.CharField(max_length=50, choices=BRACING_CHOICES, blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_dropdown_display()} ({self.qrf.qrf_no})"

class QRFWindLoading(models.Model):

    BRACING_CHOICES = [
        ("AS_PER_DESIGN", "As per design"),
        ("FULL_HT_CROSS", "Full height cross"),
        ("DIAGONAL", "Diagonal"),
        ("K_BRACE", "K-Brace"),
        ("NONE", "None"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="wind_loadings")
    name = models.CharField(max_length=100, help_text="Label, e.g. 'Roof member'")
    dropdown = models.CharField(max_length=50, choices=BRACING_CHOICES, blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_dropdown_display()} ({self.qrf.qrf_no})"
    

class QRFGravityLoading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="gravity_loadings")
    name = models.CharField(max_length=100, help_text="Label, e.g. 'Roof member'")
    load_value = models.CharField(max_length=100, help_text="Label, e.g. 'Roof member'")
    unit = models.CharField(max_length=100, help_text="Label, e.g. 'Roof member'")
    location = models.CharField(max_length=100, help_text="Label, e.g. 'Roof member'")
    


    def __str__(self):
        return f"{self.name} - ({self.qrf.qrf_no})"
    

class QRFBuildingAddition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="additional")
    name = models.CharField(max_length=100, help_text="Label, e.g. 'Roof member'")
    value = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - ({self.qrf.qrf_no})"
    
class QRFSheetingDetail(models.Model):
    """
    Dynamic table for 'Sheeting & Gutter Down Takes' section.
    Each record represents one line (e.g. Roof Sheeting, Gutter, Ridge Vent).
    """

    SHEETING_CHOICES = [
        ("AS_PER_DESIGN", "As per design"),
        ("GALVALUME", "Galvalume"),
        ("TCT_COLOR", "TCT Color"),
        ("0.47_TCT", "0.475mm thk TCT Color"),
        ("0.50_TCT", "0.50mm thk TCT Color"),
        ("0.50_TCT_LINER", "0.50mm thk TCT Color Liner"),
        ("N_A", "N/A"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="sheeting_details")

    # Each row
    name = models.CharField(
        max_length=100,
        help_text="Label like 'Roof Sheeting', 'Gutter', 'Ridge Vent', etc."
    )
    specification = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. '0.475mm thk TCT Color' or 'Galvalume pipe'"
    )
    additional_requirement = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. 'Sub purlin requirement', 'Header pipe arrangement'"
    )
    mesh = models.BooleanField(default=False, help_text="Is mesh required?")
    insulation = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional e.g. 'Mesh', 'Fiber', etc."
    )
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} - {self.qrf.qrf_no}"


class QRFCanopy(models.Model):
    """
    Canopy details table.
    Each QRF can have multiple canopy rows.
    """
    TYPE_CHOICES = [
        ("SLOPE_AWAY", "Slope away from building"),
        ("SLOPE_TOWARDS", "Slope towards building"),
        ("FLAT", "Flat"),
        ("CUSTOM", "Custom"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="canopies")
    location = models.CharField(max_length=100, blank=True)
    nos = models.PositiveIntegerField(null=True, blank=True)
    length_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    clear_height_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    type_of_canopy = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True)
    soffit_required = models.BooleanField(default=False)
    gutter_and_downtake = models.BooleanField(default=False)

    remarks = models.TextField(blank=True)


    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Canopy @ {self.location or 'N/A'} ({self.qrf.qrf_no})"


class QRFFramedOpening(models.Model):
    """
    Framed Opening details table.
    Each QRF can have multiple framed openings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="framed_openings")

    location = models.CharField(max_length=100, blank=True)
    nos = models.PositiveIntegerField(null=True, blank=True)
    width_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    door_type = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Framed Opening @ {self.location or 'N/A'} ({self.qrf.qrf_no})"


class QRFMezzanine(models.Model):
    """
    Mezzanine floor details table.
    Each QRF can have multiple mezzanine entries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="mezzanines")

    location = models.CharField(max_length=100, blank=True)
    ll_kn_sqm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Live Load (kN/sqm)")
    dl_kn_sqm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Dead Load (kN/sqm)")
    cl_kn_sqm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Collateral Load (kN/sqm)")

    height_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    slab_thk_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Slab Thickness (mm)")

    including_deck = models.BooleanField(default=False, help_text="True = Including Deck, False = Excluding Deck")
    deck_sheet_thk_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Deck Sheet Thickness (mm)")

    handrails = models.BooleanField(default=False)
    nos_of_staircase = models.PositiveIntegerField(null=True, blank=True)
    staircase_treads = models.CharField(max_length=100, blank=True)
    shear_studs = models.BooleanField(default=False)

    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Mezzanine @ {self.location or 'N/A'} ({self.qrf.qrf_no})"

class QRFCrane(models.Model):
    """
    Crane details table.
    Each QRF can have multiple crane entries.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="cranes")

    type = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    capacity_mt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    nos = models.PositiveIntegerField(null=True, blank=True)
    span_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    height_reference = models.CharField(max_length=100, blank=True, help_text="Top of crane beam, etc.")
    tandem_operation = models.BooleanField(default=False)
    walkway = models.BooleanField(default=False)
    walkway_width_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    walkway_handrail = models.BooleanField(default=False)
    cage_ladder = models.BooleanField(default=False)
    crane_beam_by = models.CharField(max_length=100, blank=True)

    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Crane @ {self.location or 'N/A'} ({self.qrf.qrf_no})"


class QRFFascia(models.Model):
    """
    Fascia details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="fascias")

    location = models.CharField(max_length=100, blank=True)
    type_of_fascia = models.CharField(max_length=100, blank=True)
    fascia_upto = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Fascia @ {self.location or 'N/A'} ({self.qrf.qrf_no})"

class QRFPartitionWall(models.Model):
    """
    Partition wall details table.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="partition_walls")

    location = models.CharField(max_length=100, blank=True)
    length_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    type_of_sheeting = models.CharField(max_length=100, blank=True)
    single_or_double_side = models.CharField(max_length=50, blank=True)
    permanent_or_removable = models.CharField(max_length=50, blank=True)
    bwall_condition = models.CharField(max_length=100, blank=True)
    girt_condition = models.CharField(max_length=100, blank=True)
    insulation = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Partition Wall @ {self.location or 'N/A'} ({self.qrf.qrf_no})"

class QRFRoofMonitor(models.Model):
    """
    Roof monitor details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="roof_monitors")

    location = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    length_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    acph = models.CharField(max_length=50, blank=True, help_text="Air changes per hour")
    louvers = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Roof Monitor @ {self.location or 'N/A'} ({self.qrf.qrf_no})"

class QRFLouver(models.Model):
    """
    Louver details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="louvers")

    location = models.CharField(max_length=100, blank=True)
    length_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    nos = models.PositiveIntegerField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Louver @ {self.location or 'N/A'} ({self.qrf.qrf_no})"

class QRFSafetyLifeLineSystem(models.Model):
    """
    Safety life line system details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="safety_life_line_systems")

    location = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Safety Life Line System @ {self.location or 'N/A'} ({self.qrf.qrf_no})"

class QRFCageLadder(models.Model):
    """
    Cage ladder details table.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="cage_ladders")

    quantity = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    height_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Cage Ladder @ {self.location or 'N/A'} ({self.qrf.qrf_no})"

class QRFPipeRackCableTray(models.Model):
    """
    Pipe rack / cable tray details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qrf = models.ForeignKey("qrf.QRF", on_delete=models.CASCADE, related_name="pipe_rack_trays")

    location = models.CharField(max_length=100, blank=True)
    height_from_ffl_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bracket_width_mm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    one_side_or_two = models.CharField(max_length=50, blank=True)
    loading_kg_per_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supporting_structure_required = models.BooleanField(default=False)
    supporting_structure_type = models.CharField(max_length=100, blank=True, help_text="e.g. Hot Rolled / Cold Formed")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Pipe Rack/Cable Tray @ {self.location or 'N/A'} ({self.qrf.qrf_no})"

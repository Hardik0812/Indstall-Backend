from .models import (
    QRFBuildingUnit,
    QRFBuildingParameter,
    QRFMinThicknessCriteria,
    QRFSecondaryDetails,
    QRFBaseCondition,
    QRFBracingCondition,
    QRFGravityLoading,
    QRFSeismicLoading,
    QRFWindLoading,
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

def initialize_qrf_dependencies(qrf):
    """
    Auto-creates all related child objects for a new QRF.
    Populates building units (Main + Lean-To 1 + Lean-To 2),
    parameters, loadings, conditions, additions, and accessories.
    """

    # ------------------------------------------------------------------
    # 0️⃣ BUILDING UNITS & PARAMETERS
    # ------------------------------------------------------------------

    building_templates = [
        {
            "unit_type": "MAIN",
            "name": "Main Building",
            "frame_type": "RF",
            "order": 1,
            "default_end_condition": "C/C_COL",
        },
        {
            "unit_type": "LEAN_TO",
            "name": "Lean To Shed - 1",
            "frame_type": "LEAN_TO",
            "order": 2,
            "default_end_condition": "C/C_COL",
        },
        {
            "unit_type": "LEAN_TO",
            "name": "Lean To Shed - 2",
            "frame_type": "LEAN_TO",
            "order": 3,
            "default_end_condition": "C/C_COL",
        },
    ]

    # Parameters to create for each unit
    parameter_rows = [
        {"type": "WIDTH", "unit": "meter"},
        {"type": "LENGTH", "unit": "meter"},
        {"type": "CLEAR_HEIGHT", "unit": "meter"},
        {"type": "BASE_PLATE", "unit": "meter"},
        {"type": "ROOF_SLOPE", "unit": "degree"},
        {"type": "BAY_SPACING", "unit": "meter"},
        {"type": "INTERNAL_COLUMN", "unit": "meter"},
        {"type": "END_WALL_COLUMN", "unit": "meter"},
        {"type": "BWALL_FRONT", "unit": "text"},
        {"type": "BWALL_BACK", "unit": "text"},
        {"type": "BWALL_LEFT", "unit": "text"},
        {"type": "BWALL_RIGHT", "unit": "text"},
        {"type": "FUTURE_EXPANSION", "unit": "text"},
        {"type": "ROOF_EXTENSION", "unit": "text"},
    ]

    for unit in building_templates:
        bu = QRFBuildingUnit.objects.create(
            qrf=qrf,
            unit_type=unit["unit_type"],
            name=unit["name"],
            frame_type=unit["frame_type"],
            order=unit["order"],
        )

        for param in parameter_rows:
            QRFBuildingParameter.objects.create(
                building_unit=bu,
                parameter_type=param["type"],
                unit=param["unit"],
                end_condition=unit["default_end_condition"] if param["type"] in ["WIDTH", "LENGTH"] else "",
            )

    # ------------------------------------------------------------------
    # 1️⃣ MIN THICKNESS CRITERIA
    # ------------------------------------------------------------------
    for name in ["B/U Web", "B/U Flange", "Eave Strut", "Rafter", "Column"]:
        QRFMinThicknessCriteria.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 2️⃣ SECONDARY DETAILS
    # ------------------------------------------------------------------
    for name in ["Purlin Spacing", "Girt Spacing", "Sag Rod", "Bracing", "Ridge Line"]:
        QRFSecondaryDetails.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 3️⃣ BASE CONDITIONS
    # ------------------------------------------------------------------
    for name in ["Main Col Bases", "CB Col Bases", "Canopy Col Bases"]:
        QRFBaseCondition.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 4️⃣ BRACING CONDITIONS
    # ------------------------------------------------------------------
    for name in ["Roof Member", "Wall Member", "Side Wall"]:
        QRFBracingCondition.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 5️⃣ LOADINGS
    # ------------------------------------------------------------------
    QRFGravityLoading.objects.create(
        qrf=qrf, name="Roof DL", load_value="0.5", unit="kN/m²", location="Roof"
    )
    QRFSeismicLoading.objects.create(qrf=qrf, name="Zone", dropdown="AS_PER_DESIGN")
    QRFWindLoading.objects.create(qrf=qrf, name="Basic Wind Speed", dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 6️⃣ BUILDING ADDITIONS
    # ------------------------------------------------------------------
    for name in ["Crane", "Mezzanine", "Canopy", "Roof Monitor", "Louver", "Fascia", "Partition Wall", "Pipe Rack"]:
        QRFBuildingAddition.objects.create(qrf=qrf, name=name, value=False)

    # ------------------------------------------------------------------
    # 7️⃣ SHEETING DETAILS
    # ------------------------------------------------------------------
    for name in ["Roof Sheeting", "Wall Sheeting", "Ridge Vent", "Gutter", "Down Take"]:
        QRFSheetingDetail.objects.create(qrf=qrf, name=name, specification="", remarks="")

    # ------------------------------------------------------------------
    # 8️⃣ OTHER STRUCTURES
    # ------------------------------------------------------------------
    QRFCanopy.objects.create(qrf=qrf, location="Front", nos=1)
    QRFFramedOpening.objects.create(qrf=qrf, location="Side A", nos=1)
    QRFMezzanine.objects.create(qrf=qrf, location="Center Bay")
    QRFCrane.objects.create(qrf=qrf, location="Main Bay")
    QRFFascia.objects.create(qrf=qrf, location="Entrance")
    QRFPartitionWall.objects.create(qrf=qrf, location="Left Wing")
    QRFRoofMonitor.objects.create(qrf=qrf, location="Main Roof")
    QRFLouver.objects.create(qrf=qrf, location="Side Wall")
    QRFSafetyLifeLineSystem.objects.create(qrf=qrf, location="Roof Access")
    QRFCageLadder.objects.create(qrf=qrf, location="North Side", quantity=1)
    QRFPipeRackCableTray.objects.create(qrf=qrf, location="Utility Area")

    print(f"✅ Initialized default dependencies for QRF {qrf.qrf_no} (Main + 2 Lean-To Sheds)")

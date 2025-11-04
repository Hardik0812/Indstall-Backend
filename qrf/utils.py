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
    This populates building units, parameters, loadings, conditions,
    additions, and accessory structures.
    """

    # ------------------------------------------------------------------
    # 0️⃣  BUILDING UNITS & PARAMETERS
    # ------------------------------------------------------------------
    default_units = [
        {
            "unit_type": "MAIN",
            "name": "Main Building",
            "frame_type": "RF",
            "order": 1,
            "parameters": [
                {"parameter_type": "WIDTH", "dimension_value": 30, "unit": "meter"},
                {"parameter_type": "LENGTH", "dimension_value": 50, "unit": "meter"},
                {"parameter_type": "CLEAR_HEIGHT", "dimension_value": 10, "unit": "meter"},
                {"parameter_type": "ROOF_SLOPE", "dimension_value": 10, "unit": "degree"},
                {"parameter_type": "BAY_SPACING", "dimension_value": 6, "unit": "meter"},
                {"parameter_type": "FUTURE_EXPANSION", "text_value": "None"},
            ],
        },
        {
            "unit_type": "LEAN_TO",
            "name": "Lean-To Shed",
            "frame_type": "LEAN_TO",
            "order": 2,
            "parameters": [
                {"parameter_type": "WIDTH", "dimension_value": 10, "unit": "meter"},
                {"parameter_type": "LENGTH", "dimension_value": 20, "unit": "meter"},
                {"parameter_type": "CLEAR_HEIGHT", "dimension_value": 6, "unit": "meter"},
                {"parameter_type": "ROOF_SLOPE", "dimension_value": 8, "unit": "degree"},
                {"parameter_type": "BAY_SPACING", "dimension_value": 5, "unit": "meter"},
            ],
        },
    ]

    for unit in default_units:
        building_unit = QRFBuildingUnit.objects.create(
            qrf=qrf,
            unit_type=unit["unit_type"],
            name=unit["name"],
            frame_type=unit["frame_type"],
            order=unit["order"],
        )
        for param in unit["parameters"]:
            QRFBuildingParameter.objects.create(
                building_unit=building_unit,
                parameter_type=param["parameter_type"],
                dimension_value=param.get("dimension_value"),
                text_value=param.get("text_value", ""),
                unit=param.get("unit", ""),
            )

    # ------------------------------------------------------------------
    # 1️⃣  MIN THICKNESS CRITERIA
    # ------------------------------------------------------------------
    for name in ["B/U Web", "B/U Flange", "Eave Strut", "Rafter", "Column"]:
        QRFMinThicknessCriteria.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 2️⃣  SECONDARY DETAILS
    # ------------------------------------------------------------------
    for name in ["Purlin Spacing", "Girt Spacing", "Sag Rod", "Bracing", "Ridge Line"]:
        QRFSecondaryDetails.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 3️⃣  BASE CONDITIONS
    # ------------------------------------------------------------------
    for name in ["Main Col Bases", "CB Col Bases", "Canopy Col Bases"]:
        QRFBaseCondition.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 4️⃣  BRACING CONDITIONS
    # ------------------------------------------------------------------
    for name in ["Roof Member", "Wall Member", "Side Wall"]:
        QRFBracingCondition.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 5️⃣  LOADINGS
    # ------------------------------------------------------------------
    QRFGravityLoading.objects.create(
        qrf=qrf, name="Roof DL", load_value="0.5", unit="kN/m²", location="Roof"
    )
    QRFSeismicLoading.objects.create(qrf=qrf, name="Zone", dropdown="AS_PER_DESIGN")
    QRFWindLoading.objects.create(qrf=qrf, name="Basic Wind Speed", dropdown="AS_PER_DESIGN")

    # ------------------------------------------------------------------
    # 6️⃣  BUILDING ADDITIONS
    # (model related_name is 'additional')
    # ------------------------------------------------------------------
    for name in ["Crane", "Mezzanine", "Canopy", "Roof Monitor",
                 "Louver", "Fascia", "Partition Wall", "Pipe Rack"]:
        QRFBuildingAddition.objects.create(qrf=qrf, name=name, value=False)

    # ------------------------------------------------------------------
    # 7️⃣  SHEETING DETAILS
    # ------------------------------------------------------------------
    for name in ["Roof Sheeting", "Wall Sheeting", "Ridge Vent", "Gutter", "Down Take"]:
        QRFSheetingDetail.objects.create(qrf=qrf, name=name, specification="", remarks="")

    # ------------------------------------------------------------------
    # 8️⃣  OTHER STRUCTURES
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

    print(f"✅ Initialized ALL default dependencies (including building units) for QRF {qrf.qrf_no}")

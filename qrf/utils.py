# apps/qrf/utils.py
from .models import (
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
    """
    # --- 1. Min Thickness Criteria ---
    thickness_items = [
        "B/U Web", "B/U Flange", "Eave Strut", "Rafter", "Column"
    ]
    for name in thickness_items:
        QRFMinThicknessCriteria.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # --- 2. Secondary Details ---
    secondary_items = [
        "Purlin Spacing", "Girt Spacing", "Sag Rod", "Bracing", "Ridge Line"
    ]
    for name in secondary_items:
        QRFSecondaryDetails.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # --- 3. Base Conditions ---
    base_items = ["Main Col Bases", "CB Col Bases", "Canopy Col Bases"]
    for name in base_items:
        QRFBaseCondition.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # --- 4. Bracing Conditions ---
    bracing_items = ["Roof Member", "Wall Member", "Side Wall"]
    for name in bracing_items:
        QRFBracingCondition.objects.create(qrf=qrf, name=name, dropdown="AS_PER_DESIGN")

    # --- 5. Loadings ---
    QRFGravityLoading.objects.create(qrf=qrf, name="Roof DL", load_value="0.5", unit="kN/m²", location="Roof")
    QRFSeismicLoading.objects.create(qrf=qrf, name="Zone", dropdown="AS_PER_DESIGN")
    QRFWindLoading.objects.create(qrf=qrf, name="Basic Wind Speed", dropdown="AS_PER_DESIGN")

    # --- 6. Building Additions ---
    additions = ["Crane", "Mezzanine", "Canopy", "Roof Monitor", "Louver", "Fascia", "Partition Wall", "Pipe Rack"]
    for name in additions:
        QRFBuildingAddition.objects.create(qrf=qrf, name=name, value=False)

    # --- 7. Sheeting Details ---
    sheeting_items = ["Roof Sheeting", "Wall Sheeting", "Ridge Vent", "Gutter", "Down Take"]
    for name in sheeting_items:
        QRFSheetingDetail.objects.create(qrf=qrf, name=name, specification="", remarks="")

    # --- 8. Other structures ---
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

    print(f"✅ Initialized default dependencies for QRF {qrf.qrf_no}")

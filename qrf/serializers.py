from rest_framework import serializers
from .models import (
    QRF,
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

class QRFListSerializer(serializers.ModelSerializer):
    sales_engineer = serializers.SerializerMethodField()
    sales_region = serializers.SerializerMethodField()
    
    class Meta:
        model = QRF
        fields = [
            "id",
            "qrf_no",
            "client_name",
            "consultant_name",
            "sales_engineer",
            "sales_region",
            "job_site",
            "status",
        ]

    def get_sales_engineer(self, obj):
        """Return sales engineer's full name or username."""
        return getattr(obj.sales_engineer, "first_name", None) or getattr(obj.sales_engineer, "full_name", None) or getattr(obj.sales_engineer, "username", None)

    def get_sales_region(self, obj):
        """Return region name if available."""
        return getattr(obj.sales_region, "name", None)
    
class QRFBuildingParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFBuildingParameter
        fields = [
            "id",
            "parameter_type",
            "dimension_value",
            "text_value",
            "unit",
            "end_condition",
            "extra_data",
        ]


class QRFBuildingUnitSerializer(serializers.ModelSerializer):
    parameters = QRFBuildingParameterSerializer(many=True)

    class Meta:
        model = QRFBuildingUnit
        fields = [
            "id",
            "unit_type",
            "name",
            "frame_type",
            "order",
            "parameters",
        ]

    def create(self, validated_data):
        parameters_data = validated_data.pop("parameters", [])
        building_unit = QRFBuildingUnit.objects.create(**validated_data)
        for param_data in parameters_data:
            QRFBuildingParameter.objects.create(building_unit=building_unit, **param_data)
        return building_unit

    def update(self, instance, validated_data):
        parameters_data = validated_data.pop("parameters", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create parameters
        existing_ids = [p.id for p in instance.parameters.all()]
        sent_ids = [p.get("id") for p in parameters_data if p.get("id")]

        # Delete parameters not included
        for pid in set(existing_ids) - set(sent_ids):
            QRFBuildingParameter.objects.filter(id=pid).delete()

        for param_data in parameters_data:
            param_id = param_data.get("id", None)
            if param_id:
                param_instance = QRFBuildingParameter.objects.get(id=param_id, building_unit=instance)
                for attr, value in param_data.items():
                    setattr(param_instance, attr, value)
                param_instance.save()
            else:
                QRFBuildingParameter.objects.create(building_unit=instance, **param_data)

        return instance


class QRFSerializer(serializers.ModelSerializer):
    building_units = QRFBuildingUnitSerializer(many=True, required=False)

    class Meta:
        model = QRF
        fields = [
            "id",
            "qrf_no",
            "revision",
            "revision_date",
            "client_name",
            "consultant_name",
            "sales_engineer",
            "sales_region",
            "job_site",
            "status",
            "design_code",
            "serviceability_code",
            "building_units",
        ]
        read_only_fields = ["qrf_no"]

    def create(self, validated_data):
        building_units_data = validated_data.pop("building_units", [])

        # Pull auto-generated qrf_no from serializer instance (set in view)
        qrf_no = getattr(self, "qrf_no", None)
        if not qrf_no:
            raise ValueError("qrf_no must be set before saving QRF")

        # Inject qrf_no manually into validated_data
        validated_data["qrf_no"] = qrf_no

        qrf = QRF.objects.create(**validated_data)

        for unit_data in building_units_data:
            parameters_data = unit_data.pop("parameters", [])
            building_unit = QRFBuildingUnit.objects.create(qrf=qrf, **unit_data)
            for param_data in parameters_data:
                QRFBuildingParameter.objects.create(
                    building_unit=building_unit, **param_data
                )

        return qrf

    def update(self, instance, validated_data):
        building_units_data = validated_data.pop("building_units", [])

        # Update QRF fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle building units
        existing_ids = [u.id for u in instance.building_units.all()]
        sent_ids = [u.get("id") for u in building_units_data if u.get("id")]

        # Delete units not present in payload
        for uid in set(existing_ids) - set(sent_ids):
            QRFBuildingUnit.objects.filter(id=uid).delete()

        for unit_data in building_units_data:
            unit_id = unit_data.get("id", None)
            parameters_data = unit_data.pop("parameters", [])

            if unit_id:
                unit_instance = QRFBuildingUnit.objects.get(id=unit_id, qrf=instance)
                for attr, value in unit_data.items():
                    setattr(unit_instance, attr, value)
                unit_instance.save()

                # Update parameters via nested serializer logic
                QRFBuildingUnitSerializer().update(unit_instance, {"parameters": parameters_data})
            else:
                building_unit = QRFBuildingUnit.objects.create(qrf=instance, **unit_data)
                for param_data in parameters_data:
                    QRFBuildingParameter.objects.create(building_unit=building_unit, **param_data)

        return instance



class QRFMinThicknessCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFMinThicknessCriteria
        fields = ["id", "name", "dropdown", "qrf"]


class QRFSecondaryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFSecondaryDetails
        fields = ["id", "name", "dropdown", "qrf"]


class QRFBaseConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFBaseCondition
        fields = ["id", "name", "dropdown", "qrf"]


class QRFBracingConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFBracingCondition
        fields = ["id", "name", "dropdown", "qrf"]

class QRFGravityLoadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFGravityLoading
        fields = ["id", "name", "load_value", "unit", "location", "qrf"]


class QRFSeismicLoadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFSeismicLoading
        fields = ["id", "name", "dropdown", "qrf"]


class QRFWindLoadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFWindLoading
        fields = ["id", "name", "dropdown", "qrf"]

class QRFBuildingAdditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFBuildingAddition
        fields = ["id", "name", "value", "qrf"]

class QRFSheetingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFSheetingDetail
        fields = [
            "id",
            "name",
            "specification",
            "additional_requirement",
            "mesh",
            "insulation",
            "remarks",
            "qrf",
        ]

class QRFCanopySerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFCanopy
        fields = [
            "id",
            "location",
            "nos",
            "length_m",
            "width_m",
            "clear_height_m",
            "type_of_canopy",
            "soffit_required",
            "gutter_and_downtake",
            "remarks",
            "qrf",
        ]


class QRFFramedOpeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFFramedOpening
        fields = ["id", "location", "nos", "width_m", "height_m", "door_type", "remarks", "qrf"]


class QRFMezzanineSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFMezzanine
        fields = [
            "id",
            "location",
            "ll_kn_sqm",
            "dl_kn_sqm",
            "cl_kn_sqm",
            "height_m",
            "slab_thk_mm",
            "including_deck",
            "deck_sheet_thk_mm",
            "handrails",
            "nos_of_staircase",
            "staircase_treads",
            "shear_studs",
            "remarks",
            "qrf",
        ]


class QRFCraneSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFCrane
        fields = [
            "id",
            "type",
            "location",
            "capacity_mt",
            "nos",
            "span_m",
            "height_m",
            "height_reference",
            "tandem_operation",
            "walkway",
            "walkway_width_m",
            "walkway_handrail",
            "cage_ladder",
            "crane_beam_by",
            "remarks",
            "qrf",
        ]


class QRFFasciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFFascia
        fields = ["id", "location", "type_of_fascia", "fascia_upto", "remarks", "qrf"]


class QRFPartitionWallSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFPartitionWall
        fields = [
            "id",
            "location",
            "length_m",
            "type_of_sheeting",
            "single_or_double_side",
            "permanent_or_removable",
            "bwall_condition",
            "girt_condition",
            "insulation",
            "remarks",
            "qrf",
        ]


class QRFRoofMonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFRoofMonitor
        fields = ["id", "location", "size", "length_m", "acph", "louvers", "remarks", "qrf"]


class QRFLouverSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFLouver
        fields = ["id", "location", "length_m", "height_m", "nos", "remarks", "qrf"]


class QRFSafetyLifeLineSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFSafetyLifeLineSystem
        fields = ["id", "location", "remarks", "qrf"]


class QRFCageLadderSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFCageLadder
        fields = ["id", "quantity", "location", "height_m", "remarks", "qrf"]


class QRFPipeRackCableTraySerializer(serializers.ModelSerializer):
    class Meta:
        model = QRFPipeRackCableTray
        fields = [
            "id",
            "location",
            "height_from_ffl_m",
            "bracket_width_mm",
            "one_side_or_two",
            "loading_kg_per_m",
            "supporting_structure_required",
            "supporting_structure_type",
            "remarks",
            "qrf",
        ]

class QRFCompleteSerializer(serializers.ModelSerializer):
    """
    Full QRF serializer that includes all related tables
    (building units, parameters, criteria, loadings, etc.)
    """

    building_units = QRFBuildingUnitSerializer(many=True, read_only=True)
    min_thickness_criteria = QRFMinThicknessCriteriaSerializer(many=True, read_only=True)
    secondary_details = QRFSecondaryDetailsSerializer(many=True, read_only=True)
    base_conditions = QRFBaseConditionSerializer(many=True, read_only=True)
    bracing_conditions = QRFBracingConditionSerializer(many=True, read_only=True)
    gravity_loadings = QRFGravityLoadingSerializer(many=True, read_only=True)
    seismic_loadings = QRFSeismicLoadingSerializer(many=True, read_only=True)
    wind_loadings = QRFWindLoadingSerializer(many=True, read_only=True)
    additional = QRFBuildingAdditionSerializer(many=True, read_only=True)
    sheeting_details = QRFSheetingDetailSerializer(many=True, read_only=True)
    canopies = QRFCanopySerializer(many=True, read_only=True)
    framed_openings = QRFFramedOpeningSerializer(many=True, read_only=True)
    mezzanines = QRFMezzanineSerializer(many=True, read_only=True)
    cranes = QRFCraneSerializer(many=True, read_only=True)
    fascias = QRFFasciaSerializer(many=True, read_only=True)
    partition_walls = QRFPartitionWallSerializer(many=True, read_only=True)
    roof_monitors = QRFRoofMonitorSerializer(many=True, read_only=True)
    louvers = QRFLouverSerializer(many=True, read_only=True)
    safety_life_line_systems = QRFSafetyLifeLineSystemSerializer(many=True, read_only=True)
    cage_ladders = QRFCageLadderSerializer(many=True, read_only=True)
    pipe_rack_trays = QRFPipeRackCableTraySerializer(many=True, read_only=True)

    class Meta:
        model = QRF
        fields = [
            "id",
            "qrf_no",
            "revision",
            "revision_date",
            "client_name",
            "consultant_name",
            "sales_engineer",
            "sales_region",
            "job_site",
            "status",
            "design_code",
            "serviceability_code",
            "building_units",
            "min_thickness_criteria",
            "secondary_details",
            "base_conditions",
            "bracing_conditions",
            "gravity_loadings",
            "seismic_loadings",
            "wind_loadings",
            "additional",
            "sheeting_details",
            "canopies",
            "framed_openings",
            "mezzanines",
            "cranes",
            "fascias",
            "partition_walls",
            "roof_monitors",
            "louvers",
            "safety_life_line_systems",
            "cage_ladders",
            "pipe_rack_trays",
        ]

class QRFCompleteUpdateSerializer(serializers.ModelSerializer):
    """
    Used for CREATE and UPDATE operations with full nested data support.
    Handles all related tables intelligently.
    """
    building_units = QRFBuildingUnitSerializer(many=True, required=False)
    min_thickness_criteria = QRFMinThicknessCriteriaSerializer(many=True, required=False)
    secondary_details = QRFSecondaryDetailsSerializer(many=True, required=False)
    base_conditions = QRFBaseConditionSerializer(many=True, required=False)
    bracing_conditions = QRFBracingConditionSerializer(many=True, required=False)
    gravity_loadings = QRFGravityLoadingSerializer(many=True, required=False)
    seismic_loadings = QRFSeismicLoadingSerializer(many=True, required=False)
    wind_loadings = QRFWindLoadingSerializer(many=True, required=False)
    additional = QRFBuildingAdditionSerializer(many=True, required=False)
    sheeting_details = QRFSheetingDetailSerializer(many=True, required=False)
    canopies = QRFCanopySerializer(many=True, required=False)
    framed_openings = QRFFramedOpeningSerializer(many=True, required=False)
    mezzanines = QRFMezzanineSerializer(many=True, required=False)
    cranes = QRFCraneSerializer(many=True, required=False)
    fascias = QRFFasciaSerializer(many=True, required=False)
    partition_walls = QRFPartitionWallSerializer(many=True, required=False)
    roof_monitors = QRFRoofMonitorSerializer(many=True, required=False)
    louvers = QRFLouverSerializer(many=True, required=False)
    safety_life_line_systems = QRFSafetyLifeLineSystemSerializer(many=True, required=False)
    cage_ladders = QRFCageLadderSerializer(many=True, required=False)
    pipe_rack_trays = QRFPipeRackCableTraySerializer(many=True, required=False)

    class Meta:
        model = QRF
        fields = [
            "id", "qrf_no", "revision", "revision_date",
            "client_name", "consultant_name", "sales_engineer", "sales_region",
            "job_site", "status", "design_code", "serviceability_code",
            "building_units", "min_thickness_criteria", "secondary_details",
            "base_conditions", "bracing_conditions", "gravity_loadings",
            "seismic_loadings", "wind_loadings", "additional", "sheeting_details",
            "canopies", "framed_openings", "mezzanines", "cranes", "fascias",
            "partition_walls", "roof_monitors", "louvers",
            "safety_life_line_systems", "cage_ladders", "pipe_rack_trays"
        ]
        read_only_fields = ["id", "qrf_no"]

    def create(self, validated_data):
        """Create QRF with all nested data"""
        # Extract nested data
        nested_data = self._extract_nested_data(validated_data)
        
        # Create QRF instance
        qrf = QRF.objects.create(**validated_data)
        
        # Create all nested records
        self._create_nested_data(qrf, nested_data)
        
        return qrf

    def update(self, instance, validated_data):
        """Update QRF with all nested data"""
        # Extract nested data
        nested_data = self._extract_nested_data(validated_data)
        
        # Update QRF fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update nested data
        self._update_nested_data(instance, nested_data)
        
        return instance

    def _extract_nested_data(self, validated_data):
        """Extract all nested data from validated_data"""
        nested_fields = [
            "building_units", "min_thickness_criteria", "secondary_details",
            "base_conditions", "bracing_conditions", "gravity_loadings",
            "seismic_loadings", "wind_loadings", "additional", "sheeting_details",
            "canopies", "framed_openings", "mezzanines", "cranes", "fascias",
            "partition_walls", "roof_monitors", "louvers",
            "safety_life_line_systems", "cage_ladders", "pipe_rack_trays"
        ]
        
        nested_data = {}
        for field in nested_fields:
            if field in validated_data:
                nested_data[field] = validated_data.pop(field)
        
        return nested_data

    def _create_nested_data(self, qrf, nested_data):
        """Create all nested records for a new QRF"""
        # Handle building_units separately (has nested parameters)
        if "building_units" in nested_data:
            for unit_data in nested_data["building_units"]:
                parameters_data = unit_data.pop("parameters", [])
                unit = QRFBuildingUnit.objects.create(qrf=qrf, **unit_data)
                for param_data in parameters_data:
                    QRFBuildingParameter.objects.create(building_unit=unit, **param_data)
        
        # Handle all other nested tables
        nested_models = {
            "min_thickness_criteria": QRFMinThicknessCriteria,
            "secondary_details": QRFSecondaryDetails,
            "base_conditions": QRFBaseCondition,
            "bracing_conditions": QRFBracingCondition,
            "gravity_loadings": QRFGravityLoading,
            "seismic_loadings": QRFSeismicLoading,
            "wind_loadings": QRFWindLoading,
            "additional": QRFBuildingAddition,
            "sheeting_details": QRFSheetingDetail,
            "canopies": QRFCanopy,
            "framed_openings": QRFFramedOpening,
            "mezzanines": QRFMezzanine,
            "cranes": QRFCrane,
            "fascias": QRFFascia,
            "partition_walls": QRFPartitionWall,
            "roof_monitors": QRFRoofMonitor,
            "louvers": QRFLouver,
            "safety_life_line_systems": QRFSafetyLifeLineSystem,
            "cage_ladders": QRFCageLadder,
            "pipe_rack_trays": QRFPipeRackCableTray,
        }
        
        for field, model_class in nested_models.items():
            if field in nested_data:
                for item_data in nested_data[field]:
                    item_data.pop("id", None)  # Remove id if present
                    item_data.pop("qrf", None)  # Remove qrf if present
                    model_class.objects.create(qrf=qrf, **item_data)

    def _update_nested_data(self, qrf, nested_data):
        """Update all nested records for existing QRF"""
        # Handle building_units separately
        if "building_units" in nested_data:
            self._update_building_units(qrf, nested_data["building_units"])
        
        # Handle all other nested tables
        nested_managers = {
            "min_thickness_criteria": qrf.min_thickness_criteria,
            "secondary_details": qrf.secondary_details,
            "base_conditions": qrf.base_conditions,
            "bracing_conditions": qrf.bracing_conditions,
            "gravity_loadings": qrf.gravity_loadings,
            "seismic_loadings": qrf.seismic_loadings,
            "wind_loadings": qrf.wind_loadings,
            "additional": qrf.additional,
            "sheeting_details": qrf.sheeting_details,
            "canopies": qrf.canopies,
            "framed_openings": qrf.framed_openings,
            "mezzanines": qrf.mezzanines,
            "cranes": qrf.cranes,
            "fascias": qrf.fascias,
            "partition_walls": qrf.partition_walls,
            "roof_monitors": qrf.roof_monitors,
            "louvers": qrf.louvers,
            "safety_life_line_systems": qrf.safety_life_line_systems,
            "cage_ladders": qrf.cage_ladders,
            "pipe_rack_trays": qrf.pipe_rack_trays,
        }
        
        for field, manager in nested_managers.items():
            if field in nested_data:
                self._update_simple_nested(manager, nested_data[field])

    def _update_building_units(self, qrf, units_data):
        """Update building units with nested parameters"""
        existing_units = {str(u.id): u for u in qrf.building_units.all()}
        updated_unit_ids = []

        for unit_data in units_data:
            unit_id = str(unit_data.get("id")) if unit_data.get("id") else None
            parameters_data = unit_data.pop("parameters", [])

            if unit_id and unit_id in existing_units:
                # Update existing unit
                unit_obj = existing_units[unit_id]
                for k, v in unit_data.items():
                    if k not in ["id", "qrf"]:
                        setattr(unit_obj, k, v)
                unit_obj.save()
                updated_unit_ids.append(unit_id)
            else:
                # Create new unit
                unit_data.pop("id", None)
                unit_obj = QRFBuildingUnit.objects.create(qrf=qrf, **unit_data)
                updated_unit_ids.append(str(unit_obj.id))

            # Update parameters for this unit
            self._update_parameters(unit_obj, parameters_data)

        # Delete units not in the update
        for uid, uobj in existing_units.items():
            if uid not in updated_unit_ids:
                uobj.delete()

    def _update_parameters(self, building_unit, parameters_data):
        """Update parameters for a building unit"""
        existing_params = {str(p.id): p for p in building_unit.parameters.all()}
        updated_param_ids = []

        for param_data in parameters_data:
            param_id = str(param_data.get("id")) if param_data.get("id") else None
            
            if param_id and param_id in existing_params:
                # Update existing parameter
                param_obj = existing_params[param_id]
                for k, v in param_data.items():
                    if k not in ["id", "building_unit"]:
                        setattr(param_obj, k, v)
                param_obj.save()
                updated_param_ids.append(param_id)
            else:
                # Create new parameter
                param_data.pop("id", None)
                param_obj = QRFBuildingParameter.objects.create(
                    building_unit=building_unit,
                    **param_data
                )
                updated_param_ids.append(str(param_obj.id))

        # Delete parameters not in the update
        for pid, pobj in existing_params.items():
            if pid not in updated_param_ids:
                pobj.delete()

    def _update_simple_nested(self, related_manager, items_data):
        """Generic update for simple nested models (no further nesting)"""
        existing_objs = {str(obj.id): obj for obj in related_manager.all()}
        updated_ids = []

        for item_data in items_data:
            item_id = str(item_data.get("id")) if item_data.get("id") else None
            
            if item_id and item_id in existing_objs:
                # Update existing
                obj = existing_objs[item_id]
                for k, v in item_data.items():
                    if k not in ["id", "qrf"]:
                        setattr(obj, k, v)
                obj.save()
                updated_ids.append(item_id)
            else:
                # Create new
                item_data.pop("id", None)
                item_data.pop("qrf", None)
                related_manager.create(**item_data)

        # Delete objects not in the update
        for obj_id, obj in existing_objs.items():
            if obj_id not in updated_ids:
                obj.delete()

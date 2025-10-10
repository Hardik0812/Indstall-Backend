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
    building_units = QRFBuildingUnitSerializer(many=True)

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
        qrf = QRF.objects.create(**validated_data)
        for unit_data in building_units_data:
            parameters_data = unit_data.pop("parameters", [])
            building_unit = QRFBuildingUnit.objects.create(qrf=qrf, **unit_data)
            for param_data in parameters_data:
                QRFBuildingParameter.objects.create(building_unit=building_unit, **param_data)
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

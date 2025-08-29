from django.core.management.base import BaseCommand
from rfq_master.models import (Region, FrameType, SteelGrade, SheetingType, InsulationType, OpeningType, VentType, CraneType)

class Command(BaseCommand):
    help = "Seed all master data lookup tables (Region, FrameType, SteelGrade, etc.)"

    def handle(self, *args, **kwargs):
        datasets = {
            Region: [
                ("NORTH", "North"),
                ("SOUTH", "South"),
                ("EAST", "East"),
                ("WEST", "West"),
                ("CENTRAL", "Central"),
                ("OTHER", "Other"),
            ],
            FrameType: [
                ("SINGLE_SLOPE", "Single Slope"),
                ("MULTI_SPAN", "Multi-Span"),
                ("CLEAR_SPAN", "Clear Span"),
                ("LEAN_TO", "Lean-to"),
                ("OTHER", "Other"),
            ],
            SteelGrade: [
                ("ASTM_A36", "ASTM A36"),
                ("ASTM_A572GR50", "ASTM A572 Gr.50"),
                ("IS_2062", "IS 2062"),
                ("OTHER", "Other"),
            ],
            SheetingType: [
                ("TCT_COLOR_0.475", "TCT Color 0.475mm"),
                ("TCT_COLOR_0.50", "TCT Color 0.50mm"),
                ("TCT_BARE_0.475", "TCT Bare 0.475mm"),
                ("SSR_COLOR_0.52", "Standing Seam 0.52mm Color"),
                ("SSR_BARE_0.52", "Standing Seam 0.52mm Bare"),
                ("OTHER", "Other"),
            ],
            InsulationType: [
                ("NONE", "None"),
                ("FIBER_GLASS", "Fiber Glass"),
                ("PIR", "PIR"),
                ("EPS", "EPS"),
                ("OTHER", "Other"),
            ],
            OpeningType: [
                ("ROLLING_SHUTTER", "Rolling Shutter"),
                ("SLIDING_DOOR", "Sliding Door"),
                ("SWING_DOOR", "Swing Door"),
                ("PERSONNEL_DOOR", "Personnel Door"),
                ("WINDOW", "Window"),
                ("LOUVER", "Louver"),
                ("OTHER", "Other"),
            ],
            VentType: [
                ("NONE", "None"),
                ("RIDGE_VENT", "Ridge Vent"),
                ("TURBO_VENT", "Turbo Vent"),
                ("ROOF_MONITOR", "Roof Monitor"),
                ("OTHER", "Other"),
            ],
            CraneType: [
                ("EOT", "EOT"),
                ("MONO_RAIL", "Mono Rail"),
                ("GANTRY", "Gantry"),
                ("OTHER", "Other"),
            ],
        }

        for model, items in datasets.items():
            self.stdout.write(self.style.MIGRATE_HEADING(f"Seeding {model.__name__}..."))
            created_count = 0
            for code, name in items:
                obj, created = model.objects.get_or_create(code=code, defaults={"name": name})
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✔ Added {name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  • Already exists: {name}"))
            self.stdout.write(self.style.NOTICE(f"Done. {created_count} new {model.__name__} added.\n"))

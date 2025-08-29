from django.db import models

from rfq_master.base_model import ChoiceBase


# Create your models here.
class Region(ChoiceBase):
    """Regions for sales / projects"""

    pass


class FrameType(ChoiceBase):
    """Building frame types"""

    pass


class SteelGrade(ChoiceBase):
    """Steel material grades"""

    pass


class SheetingType(ChoiceBase):
    """Roof / wall sheeting"""

    pass


class InsulationType(ChoiceBase):
    """Insulation material types"""

    pass


class OpeningType(ChoiceBase):
    """Doors, windows, louvers"""

    pass


class VentType(ChoiceBase):
    """Ventilation systems"""

    pass


class CraneType(ChoiceBase):
    """Crane types"""

    pass

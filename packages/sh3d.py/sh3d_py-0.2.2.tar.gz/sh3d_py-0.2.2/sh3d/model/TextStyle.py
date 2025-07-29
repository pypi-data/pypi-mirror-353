import dataclasses
import enum

from javaobj import JavaObject
from .ModelBase import ModelBase
from ..BuildContext import BuildContext


@enum.unique
class Alignment(enum.Enum):
    LEFT = 'LEFT'
    CENTER = 'CENTER'
    RIGHT = 'RIGHT'

@dataclasses.dataclass
class TextStyle(ModelBase):
    font_size: float
    bold: bool
    italic: bool
    alignment: Alignment

    @classmethod
    def from_javaobj(cls, o: JavaObject, build_context: BuildContext) -> 'TextStyle':
        return cls(
            font_size=o.fontSize,
            bold=o.bold,
            italic=o.italic,
            alignment=Alignment(o.alignment.constant) if o.alignment else Alignment.CENTER
        )

    @classmethod
    def from_xml_dict(cls, data: dict, build_context: BuildContext) -> 'TextStyle':
        return cls(
            font_size=cls.required_float(data.get('@fontSize')),
            bold=False,
            italic=False,
            alignment=Alignment.CENTER
        )

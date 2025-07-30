from pydantic import BaseModel, Field

from .value_constraint import ValueConstraint
from .value_format import ValueFormat


class ValueDescriptorObject(BaseModel):
    name: str | None = Field(default=None, pattern=r'^\w+(\[\])?$')
    constraints: list[ValueConstraint] | None = None
    format: ValueFormat | None = None
    units: list[str] | None = None
    arrayDimensions: int | None = None
    metaUseOnly: bool | None = None
    jsonType: str | None = None

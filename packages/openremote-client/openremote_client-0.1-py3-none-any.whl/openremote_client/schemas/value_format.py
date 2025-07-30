from typing import Literal

from pydantic import BaseModel

date_format_type = Literal['numeric', '2-digit', 'full', 'long', 'medium', 'short', 'narrow']


class ValueFormat(BaseModel):
    useGrouping: bool | None = None
    minimumIntegerDigits: int | None = None
    minimumFractionDigits: int | None = None
    maximumFractionDigits: int | None = None
    minimumSignificantDigits: int | None = None
    maximumSignificantDigits: int | None = None
    asBoolean: bool | None = None
    asDate: bool | None = None
    asSlider: bool | None = None
    resolution: int | None = None
    dateStyle: date_format_type | None = None
    timeStyle: date_format_type | None = None
    dayPeriod: date_format_type | None = None
    hour12: bool | None = None
    iso8601: bool | None = None
    weekday: date_format_type | None = None
    era: date_format_type | None = None
    year: date_format_type | None = None
    month: date_format_type | None = None
    week: date_format_type | None = None
    day: date_format_type | None = None
    hour: date_format_type | None = None
    minute: date_format_type | None = None
    second: date_format_type | None = None
    fractionalSecondDigits: int | None = None
    timeZoneName: date_format_type | None = None
    momentJsFormat: str | None = None
    asNumber: bool | None = None
    asOnOff: bool | None = None
    asPressedReleased: bool | None = None
    asOpenClosed: bool | None = None
    asMomentary: bool | None = None
    multiline: bool | None = None

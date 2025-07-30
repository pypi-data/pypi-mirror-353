from typing import Any, Literal

from pydantic import BaseModel, Field

from .value_descriptor_object import ValueDescriptorObject

attribute_type = Literal[
    'assetID',
    'assetType',
    'boolean',
    'booleanMap',
    'bigInteger',
    'bigNumber',
    'byte',
    'calendarEvent',
    'connectionStatus',
    'consoleProviders',
    'colourRGB',
    'CRONExpression',
    'dateAndTime',
    'direction',
    'email',
    'executionStatus',
    'GEO_JSONPoint',
    'hostOrIPAddress',
    'HTTP_URL',
    'integer',
    'integerMap',
    'integerByte',
    'IPAddress',
    'JSONObject',
    'JSON',
    'long',
    'multivaluedTextMap',
    'number',
    'numberMap',
    'negativeInteger',
    'negativeNumber',
    'oAuthGrant',
    'positiveInteger',
    'positiveNumber',
    'periodDurationISO8601',
    'text',
    'textMap',
    'timestamp',
    'timestampISO8601',
    'timeDurationISO8601',
    'timeAndPeriodDurationISO8601',
    'TCP_IPPortNumber',
    'usernameAndPassword',
    'UUID',
    'WS_URL'
]


class AttributeObject(BaseModel):
    type: ValueDescriptorObject | attribute_type = None
    value: Any
    name: str = Field(pattern=r'^\w+$')
    meta: dict[str, Any] | None = None
    timestamp: int

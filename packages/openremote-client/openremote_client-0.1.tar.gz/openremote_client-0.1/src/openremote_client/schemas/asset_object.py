from datetime import datetime

from pydantic import BaseModel, Field

from .attribute_object import AttributeObject


class AssetObject(BaseModel):
    id: str | None = Field(default=None, pattern=r'^[0-9A-Za-z]{22}$')
    version: int | None = Field(default=None, ge=0)
    createdOn: datetime | None = None
    name: str = Field(min_length=1, max_length=1023)
    accessPublicRead: bool | None = None
    parentId: str | None = Field(default=None, pattern=r'^[0-9A-Za-z]{22}$')
    realm: str = Field(min_length=1, max_length=255)
    type: str | None = None
    path: list[str] | None = None
    attributes: dict[str, AttributeObject]

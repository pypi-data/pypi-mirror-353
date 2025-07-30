from pydantic import BaseModel


class ValueConstraint(BaseModel):
    message: str | None = None
    type: str

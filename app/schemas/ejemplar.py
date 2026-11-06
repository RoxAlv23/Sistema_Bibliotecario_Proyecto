
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class EjemplarCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    libro_id: int = Field(gt=0)


class EjemplarUpdate(BaseModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=50)

class EjemplarResponse(BaseModel):
    id: int
    codigo: str
    libro_id: int
    estado: str

    model_config = ConfigDict(from_attributes=True)


from pydantic import BaseModel, ConfigDict, Field


class AutorBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    nacionalidad: str | None = Field(default=None, max_length=100)


class AutorCreate(AutorBase):
    pass


class AutorResponse(AutorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

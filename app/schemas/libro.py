
from pydantic import BaseModel, ConfigDict, Field


class LibroBase(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    isbn: str | None = Field(default=None, max_length=30)
    anio_publicacion: int | None = Field(default=None, ge=1000, le=2100)
    descripcion: str | None = None
    autor_id: int = Field(gt=0)
    categoria_id: int = Field(gt=0)


class LibroCreate(LibroBase):
    pass


class LibroUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    isbn: str | None = Field(default=None, max_length=30)
    anio_publicacion: int | None = Field(default=None, ge=1000, le=2100)
    descripcion: str | None = None
    autor_id: int | None = Field(default=None, gt=0)
    categoria_id: int | None = Field(default=None, gt=0)


class LibroResponse(LibroBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

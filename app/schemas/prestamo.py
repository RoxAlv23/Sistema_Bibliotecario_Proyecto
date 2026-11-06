
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PrestamoCreate(BaseModel):
    usuario_id: int = Field(gt=0)
    ejemplar_id: int = Field(gt=0)
    fecha_devolucion_prevista: date


class PrestamoResponse(BaseModel):
    id: int
    usuario_id: int
    ejemplar_id: int
    fecha_prestamo: date
    fecha_devolucion_prevista: date
    fecha_devolucion_real: date | None
    estado: str

    model_config = ConfigDict(from_attributes=True)

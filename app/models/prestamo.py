
from sqlalchemy import Column, Integer, Date, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    ejemplar_id = Column(Integer, ForeignKey("ejemplares.id"), nullable=False)
    fecha_prestamo = Column(Date, nullable=False)
    fecha_devolucion_prevista = Column(Date, nullable=False)
    fecha_devolucion_real = Column(Date)
    estado = Column(String(20), default="activo")
    fecha_registro = Column(DateTime, server_default=func.current_timestamp())

    usuario = relationship("Usuario", back_populates="prestamos")
    ejemplar = relationship("Ejemplar", back_populates="prestamos")

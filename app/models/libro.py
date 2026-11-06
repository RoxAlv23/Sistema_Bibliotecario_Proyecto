
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Libro(Base):
    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    isbn = Column(String(30), unique=True)
    anio_publicacion = Column(Integer)
    descripcion = Column(Text)
    autor_id = Column(Integer, ForeignKey("autores.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    autor = relationship("Autor", back_populates="libros")
    categoria = relationship("Categoria", back_populates="libros")
    ejemplares = relationship("Ejemplar", back_populates="libro")

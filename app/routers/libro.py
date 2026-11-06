

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.libro import Libro
from app.models.autor import Autor
from app.models.categoria import Categoria
from app.schemas.libro import LibroCreate, LibroUpdate, LibroResponse
from app.auth.dependencies import requiere_rol

router = APIRouter(prefix="/libros", tags=["Libros"])


# REGISTRAR LIBRO
@router.post(
    "/",
    response_model=LibroResponse,
    status_code=201,
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def crear_libro(datos: LibroCreate, db: Session = Depends(get_db)):

    autor = db.query(Autor).filter(
        Autor.id == datos.autor_id
    ).first()

    categoria = db.query(Categoria).filter(
        Categoria.id == datos.categoria_id
    ).first()

    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    nuevo_libro = Libro(**datos.model_dump())
    db.add(nuevo_libro)

    try:
        db.commit()
        db.refresh(nuevo_libro)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El ISBN ya existe")

    return nuevo_libro


# LISTAR LIBROS
@router.get("/", response_model=list[LibroResponse])
def listar_libros(db: Session = Depends(get_db)):

    return db.query(Libro).all()


# CONSULTAR UN LIBRO
@router.get("/{libro_id}", response_model=LibroResponse)
def obtener_libro(libro_id: int, db: Session = Depends(get_db)):

    libro = db.query(Libro).filter(Libro.id == libro_id).first()

    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    return libro


# ACTUALIZAR LIBRO
@router.put(
    "/{libro_id}",
    response_model=LibroResponse,
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def actualizar_libro(
    libro_id: int,
    datos: LibroUpdate,
    db: Session = Depends(get_db)
):

    libro = db.query(Libro).filter(Libro.id == libro_id).first()

    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    cambios = datos.model_dump(exclude_unset=True)

    if "autor_id" in cambios:
        autor = db.query(Autor).filter(
            Autor.id == cambios["autor_id"]
        ).first()

        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado")

    if "categoria_id" in cambios:
        categoria = db.query(Categoria).filter(
            Categoria.id == cambios["categoria_id"]
        ).first()

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")

    for campo, valor in cambios.items():
        setattr(libro, campo, valor)

    try:
        db.commit()
        db.refresh(libro)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El ISBN ya existe")

    return libro


# ELIMINAR LIBRO
@router.delete(
    "/{libro_id}",
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def eliminar_libro(libro_id: int, db: Session = Depends(get_db)):

    libro = db.query(Libro).filter(Libro.id == libro_id).first()

    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    db.delete(libro)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el libro tiene ejemplares asociados."
        )

    return {"mensaje": "Libro eliminado correctamente"}

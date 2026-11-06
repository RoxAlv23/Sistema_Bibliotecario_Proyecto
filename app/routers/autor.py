
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.autor import Autor
from app.schemas.autor import AutorCreate, AutorResponse
from app.auth.dependencies import requiere_rol


router = APIRouter(prefix="/autores", tags=["Autores"])


# REGISTRAR AUTOR
@router.post(
    "/",
    response_model=AutorResponse,
    status_code=201,
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def crear_autor(datos: AutorCreate, db: Session = Depends(get_db)):

    nuevo_autor = Autor(**datos.model_dump())

    db.add(nuevo_autor)

    try:
        db.commit()
        db.refresh(nuevo_autor)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo registrar el autor."
        )

    return nuevo_autor


# CONSULTAR TODOS LOS AUTORES
@router.get("/", response_model=list[AutorResponse])
def listar_autores(db: Session = Depends(get_db)):

    return db.query(Autor).all()


# CONSULTAR UN AUTOR
@router.get("/{autor_id}", response_model=AutorResponse)
def obtener_autor(autor_id: int, db: Session = Depends(get_db)):

    autor = db.query(Autor).filter(Autor.id == autor_id).first()

    if not autor:
        raise HTTPException(
            status_code=404,
            detail="Autor no encontrado"
        )

    return autor


# ACTUALIZAR AUTOR
@router.put(
    "/{autor_id}",
    response_model=AutorResponse,
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def actualizar_autor(
    autor_id: int,
    datos: AutorCreate,
    db: Session = Depends(get_db)
):
    autor = db.query(Autor).filter(Autor.id == autor_id).first()

    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    for campo, valor in datos.model_dump().items():
        setattr(autor, campo, valor)

    db.commit()
    db.refresh(autor)

    return autor


# ELIMINAR AUTOR
@router.delete("/{autor_id}")
def eliminar_autor(autor_id: int, db: Session = Depends(get_db)):

    autor = db.query(Autor).filter(Autor.id == autor_id).first()

    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    db.delete(autor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el autor tiene libros asociados."
        )

    return {"mensaje": "Autor eliminado correctamente"}

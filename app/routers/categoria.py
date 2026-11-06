
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaResponse
from app.auth.dependencies import requiere_rol

router = APIRouter(prefix="/categorias", tags=["Categorias"])


# REGISTRAR CATEGORIA
@router.post(
    "/",
    response_model=CategoriaResponse,
    status_code=201,
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def crear_categoria(datos: CategoriaCreate, db: Session = Depends(get_db)):

    nueva = Categoria(**datos.model_dump())
    db.add(nueva)

    try:
        db.commit()
        db.refresh(nueva)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="La categoria ya existe")

    return nueva


# LISTAR CATEGORIAS
@router.get("/", response_model=list[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):

    return db.query(Categoria).all()


# CONSULTAR UNA CATEGORIA
@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):

    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    return categoria


# ACTUALIZAR CATEGORIA
@router.put(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def actualizar_categoria(
    categoria_id: int,
    datos: CategoriaCreate,
    db: Session = Depends(get_db)
):

    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    for campo, valor in datos.model_dump().items():
        setattr(categoria, campo, valor)

    try:
        db.commit()
        db.refresh(categoria)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="La categoria ya existe")

    return categoria


# ELIMINAR CATEGORIA
@router.delete(
    "/{categoria_id}",
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):

    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    db.delete(categoria)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: tiene libros asociados."
        )

    return {"mensaje": "Categoria eliminada correctamente"}

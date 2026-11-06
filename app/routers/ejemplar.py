
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.ejemplar import Ejemplar
from app.models.libro import Libro
from app.schemas.ejemplar import (
    EjemplarCreate,
    EjemplarUpdate,
    EjemplarResponse
)
from app.auth.dependencies import requiere_rol

router = APIRouter(prefix="/ejemplares", tags=["Ejemplares"])


# REGISTRAR EJEMPLAR
@router.post(
    "/",
    response_model=EjemplarResponse,
    status_code=201,
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def crear_ejemplar(datos: EjemplarCreate, db: Session = Depends(get_db)):

    libro = db.query(Libro).filter(
        Libro.id == datos.libro_id
    ).first()

    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    nuevo = Ejemplar(**datos.model_dump())

    db.add(nuevo)

    try:
        db.commit()
        db.refresh(nuevo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="El codigo del ejemplar ya existe"
        )

    return nuevo


# LISTAR EJEMPLARES
@router.get("/", response_model=list[EjemplarResponse])
def listar_ejemplares(db: Session = Depends(get_db)):

    return db.query(Ejemplar).all()


# CONSULTAR UN EJEMPLAR
@router.get("/{ejemplar_id}", response_model=EjemplarResponse)
def obtener_ejemplar(ejemplar_id: int, db: Session = Depends(get_db)):

    ejemplar = db.query(Ejemplar).filter(
        Ejemplar.id == ejemplar_id
    ).first()

    if not ejemplar:
        raise HTTPException(status_code=404, detail="Ejemplar no encontrado")

    return ejemplar


# ACTUALIZAR EJEMPLAR
@router.put(
    "/{ejemplar_id}",
    response_model=EjemplarResponse,
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def actualizar_ejemplar(
    ejemplar_id: int,
    datos: EjemplarUpdate,
    db: Session = Depends(get_db)
):

    ejemplar = db.query(Ejemplar).filter(
        Ejemplar.id == ejemplar_id
    ).first()

    if not ejemplar:
        raise HTTPException(status_code=404, detail="Ejemplar no encontrado")

    cambios = datos.model_dump(exclude_unset=True)

    # No permitir cambiar manualmente el estado si tiene un prestamo activo.
    # Los prestamos controlaran ese cambio.
    if "estado" in cambios:
        if ejemplar.estado == "prestado":
            raise HTTPException(
                status_code=409,
                detail="No se puede modificar el estado de un ejemplar prestado."
            )

    for campo, valor in cambios.items():
        setattr(ejemplar, campo, valor)

    try:
        db.commit()
        db.refresh(ejemplar)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="El codigo del ejemplar ya existe"
        )

    return ejemplar


# ELIMINAR EJEMPLAR
@router.delete(
    "/{ejemplar_id}",
    dependencies=[Depends(requiere_rol("administrador", "bibliotecario"))]
)
def eliminar_ejemplar(ejemplar_id: int, db: Session = Depends(get_db)):

    ejemplar = db.query(Ejemplar).filter(
        Ejemplar.id == ejemplar_id
    ).first()

    if not ejemplar:
        raise HTTPException(status_code=404, detail="Ejemplar no encontrado")

    if ejemplar.estado == "prestado":
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar un ejemplar prestado."
        )

    db.delete(ejemplar)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el ejemplar tiene prestamos registrados."
        )

    return {"mensaje": "Ejemplar eliminado correctamente"}

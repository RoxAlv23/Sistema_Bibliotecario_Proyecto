
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.prestamo import Prestamo
from app.models.usuario import Usuario
from app.models.ejemplar import Ejemplar
from app.schemas.prestamo import (
    PrestamoCreate,
    PrestamoResponse
)
from app.auth.dependencies import (
    obtener_usuario_actual,
    requiere_rol
)


router = APIRouter(
    prefix="/prestamos",
    tags=["Préstamos y devoluciones"]
)


# REGISTRAR UN PRÉSTAMO
@router.post(
    "/",
    response_model=PrestamoResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_prestamo(
    datos: PrestamoCreate,
    db: Session = Depends(get_db),
    personal=Depends(
        requiere_rol("administrador", "bibliotecario")
    )
):
    # Validar fecha de devolución
    if datos.fecha_devolucion_prevista <= date.today():
        raise HTTPException(
            status_code=400,
            detail="La fecha de devolución debe ser futura"
        )

    # Verificar que el usuario exista y esté activo
    usuario = db.query(Usuario).filter(
        Usuario.id == datos.usuario_id
    ).first()

    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado o inactivo"
        )

    try:
        # Bloquear el ejemplar durante la operación
        ejemplar = db.query(Ejemplar).filter(
            Ejemplar.id == datos.ejemplar_id
        ).with_for_update().first()

        if not ejemplar:
            raise HTTPException(
                status_code=404,
                detail="Ejemplar no encontrado"
            )

        # Comprobar disponibilidad
        if ejemplar.estado != "disponible":
            raise HTTPException(
                status_code=409,
                detail="El ejemplar no está disponible para préstamo"
            )

        nuevo_prestamo = Prestamo(
            usuario_id=datos.usuario_id,
            ejemplar_id=datos.ejemplar_id,
            fecha_prestamo=date.today(),
            fecha_devolucion_prevista=datos.fecha_devolucion_prevista,
            estado="activo"
        )

        ejemplar.estado = "prestado"

        db.add(nuevo_prestamo)
        db.commit()
        db.refresh(nuevo_prestamo)

        return nuevo_prestamo

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se pudo registrar el préstamo"
        )


# CONSULTAR TODOS LOS PRÉSTAMOS
@router.get(
    "/",
    response_model=list[PrestamoResponse]
)
def listar_prestamos(
    db: Session = Depends(get_db),
    personal=Depends(
        requiere_rol("administrador", "bibliotecario")
    )
):
    return db.query(Prestamo).order_by(
        Prestamo.id.desc()
    ).all()


# CONSULTAR PRÉSTAMOS ACTIVOS
@router.get(
    "/activos",
    response_model=list[PrestamoResponse]
)
def listar_prestamos_activos(
    db: Session = Depends(get_db),
    personal=Depends(
        requiere_rol("administrador", "bibliotecario")
    )
):
    return db.query(Prestamo).filter(
        Prestamo.estado == "activo"
    ).all()


# CONSULTAR MIS PRÉSTAMOS
@router.get(
    "/mis-prestamos",
    response_model=list[PrestamoResponse]
)
def mis_prestamos(
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual)
):
    return db.query(Prestamo).filter(
        Prestamo.usuario_id == usuario.id
    ).order_by(Prestamo.id.desc()).all()


# CONSULTAR UN PRÉSTAMO POR ID
@router.get(
    "/{prestamo_id}",
    response_model=PrestamoResponse
)
def obtener_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual)
):
    prestamo = db.query(Prestamo).filter(
        Prestamo.id == prestamo_id
    ).first()

    if not prestamo:
        raise HTTPException(
            status_code=404,
            detail="Préstamo no encontrado"
        )

    # El usuario normal solo puede consultar sus préstamos
    if (
        usuario.rol.nombre == "usuario"
        and prestamo.usuario_id != usuario.id
    ):
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para consultar este préstamo"
        )

    return prestamo


# REGISTRAR DEVOLUCIÓN
@router.post("/{prestamo_id}/devolucion")
def registrar_devolucion(
    prestamo_id: int,
    db: Session = Depends(get_db),
    personal=Depends(
        requiere_rol("administrador", "bibliotecario")
    )
):
    prestamo = db.query(Prestamo).filter(
        Prestamo.id == prestamo_id
    ).first()

    if not prestamo:
        raise HTTPException(
            status_code=404,
            detail="Préstamo no encontrado"
        )

    if prestamo.estado == "devuelto":
        raise HTTPException(
            status_code=409,
            detail="Este préstamo ya fue devuelto"
        )

    ejemplar = db.query(Ejemplar).filter(
        Ejemplar.id == prestamo.ejemplar_id
    ).with_for_update().first()

    if not ejemplar:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el ejemplar asociado"
        )

    prestamo.estado = "devuelto"
    prestamo.fecha_devolucion_real = date.today()
    ejemplar.estado = "disponible"

    db.commit()

    return {
        "mensaje": "Devolución registrada correctamente",
        "prestamo_id": prestamo.id,
        "ejemplar_id": ejemplar.id,
        "estado_ejemplar": ejemplar.estado,
        "fecha_devolucion_real": str(date.today())
    }


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse
)
from app.auth.security import generar_password_hash
from app.auth.dependencies import requiere_rol


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


# REGISTRAR USUARIO
@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_usuario(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
    administrador=Depends(requiere_rol("administrador"))
):
    existente = db.query(Usuario).filter(
        Usuario.correo == datos.correo
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    if len(datos.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="La contraseña no puede superar 72 bytes"
        )

    rol = db.query(Rol).filter(
        Rol.id == datos.rol_id
    ).first()

    if not rol:
        raise HTTPException(
            status_code=404,
            detail="El rol indicado no existe"
        )

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        apellido=datos.apellido,
        correo=datos.correo,
        password_hash=generar_password_hash(datos.password),
        rol_id=datos.rol_id,
        activo=True
    )

    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        return nuevo_usuario

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se pudo registrar el usuario"
        )


# LISTAR USUARIOS
@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    administrador=Depends(requiere_rol("administrador"))
):
    return db.query(Usuario).all()


# CONSULTAR USUARIO POR ID
@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    administrador=Depends(requiere_rol("administrador"))
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return usuario


# ACTUALIZAR USUARIO
@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    administrador=Depends(requiere_rol("administrador"))
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    cambios = datos.model_dump(exclude_unset=True)

    if usuario.id == administrador.id and cambios.get("activo") is False:
        raise HTTPException(
            status_code=400,
            detail="No puedes desactivar tu propia cuenta"
        )

    if "correo" in cambios:
        existente = db.query(Usuario).filter(
            Usuario.correo == cambios["correo"],
            Usuario.id != usuario_id
        ).first()

        if existente:
            raise HTTPException(
                status_code=400,
                detail="El correo ya pertenece a otro usuario"
            )

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    try:
        db.commit()
        db.refresh(usuario)
        return usuario

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se pudo actualizar el usuario"
        )


# ELIMINAR USUARIO
@router.delete("/{usuario_id}")
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    administrador=Depends(requiere_rol("administrador"))
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    if usuario.id == administrador.id:
        raise HTTPException(
            status_code=400,
            detail="No puedes eliminar tu propia cuenta"
        )

    try:
        db.delete(usuario)
        db.commit()

        return {
            "mensaje": "Usuario eliminado correctamente"
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar porque tiene préstamos registrados"
        )

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import get_db
from app.models.usuario import Usuario
from app.auth.security import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    error_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        datos = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        usuario_id = datos.get("sub")

        if usuario_id is None:
            raise error_credenciales

        usuario_id = int(usuario_id)

    except (JWTError, ValueError, TypeError):
        raise error_credenciales

    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if usuario is None:
        raise error_credenciales

    if not usuario.activo:
        raise HTTPException(
            status_code=403,
            detail="El usuario está desactivado"
        )

    return usuario


def requiere_rol(*roles_permitidos):
    def verificar_rol(
        usuario: Usuario = Depends(obtener_usuario_actual)
    ):
        if usuario.rol.nombre not in roles_permitidos:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para realizar esta acción"
            )

        return usuario

    return verificar_rol
from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext


load_dotenv()

# Configuración para proteger contraseñas
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# Configuración de tokens
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)


def verificar_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def generar_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def crear_token_acceso(datos: dict) -> str:
    datos_token = datos.copy()

    fecha_expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    datos_token.update({
        "exp": fecha_expiracion
    })

    return jwt.encode(
        datos_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
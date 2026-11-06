
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

from app.routers import autor, categoria, libro, ejemplar, auth, usuario, prestamo

from app.auth.dependencies import requiere_rol

app = FastAPI(
    title="Sistema Bibliotecario",
    description="API REST para administrar una biblioteca",
    version="1.0.0"
)

# Registrar las rutas de la API
app.include_router(autor.router)
app.include_router(categoria.router)
app.include_router(libro.router)
app.include_router(ejemplar.router)
app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(prestamo.router)


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido al Sistema Bibliotecario",
        "estado": "API funcionando"
    }


@app.get("/prueba-db")
def probar_conexion(db: Session = Depends(get_db)):
    resultado = db.execute(
        text("SELECT DATABASE()")
    ).scalar()

    return {
        "mensaje": "Conexion exitosa con MySQL",
        "base_de_datos": resultado
    }

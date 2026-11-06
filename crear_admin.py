from getpass import getpass

from app.database import SessionLocal
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.auth.security import generar_password_hash


def crear_administrador():
    db = SessionLocal()

    try:
        print("\n=== CREAR ADMINISTRADOR ===")

        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        correo = input("Correo electrónico: ").strip().lower()

        password = getpass("Contraseña: ")
        confirmar = getpass("Confirmar contraseña: ")

        if not nombre or not apellido or not correo:
            print("Todos los campos son obligatorios.")
            return

        if len(password.encode("utf-8")) > 72:
            print("La contraseña no puede superar 72 bytes.")
            return

        if len(password) < 8:
            print("La contraseña debe tener al menos 8 caracteres.")
            return

        if password != confirmar:
            print("Las contraseñas no coinciden.")
            return

        existente = db.query(Usuario).filter(
            Usuario.correo == correo
        ).first()

        if existente:
            print("Ya existe un usuario con ese correo.")
            return

        rol = db.query(Rol).filter(
            Rol.nombre == "administrador"
        ).first()

        if not rol:
            print("No existe el rol administrador en la base de datos.")
            return

        nuevo_admin = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            password_hash=generar_password_hash(password),
            rol_id=rol.id,
            activo=True
        )

        db.add(nuevo_admin)
        db.commit()

        print("\nAdministrador creado correctamente.")
        print("Correo:", correo)

    except Exception as error:
        db.rollback()
        print("Ocurrió un error:", error)

    finally:
        db.close()


if __name__ == "__main__":
    crear_administrador()
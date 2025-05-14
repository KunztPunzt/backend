from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from backend.utilidades.config import settings
# Llamada directorios del proyecto
from backend.modelos.usuario import Usuario
from backend.dtos.usuarioRegistroDto import UsuarioCrear
from backend.servicios.baseDatos import Base
from backend.utilidades.seguridad import hash_password, verify_password

def crear_usuario(db: Session, usuario: UsuarioCrear):
    # Crear el usuario en estado “pendiente”
    db_usuario = Usuario(
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        email=usuario.email,
        password=hash_password(usuario.password), 
        rol=usuario.rol,
        estadoCuenta="pendiente",
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    # Generar token JWT con expiración
    expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    token = jwt.encode(
        {"sub": db_usuario.email, "exp": expire},
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    db_usuario.tokenActivacion = token
    db.commit()

    return db_usuario


# Para el registro
def obtener_por_email(db: Session, email: str):
    """Busca un usuario por su email y retorna el objeto Usuario o None si no existe."""
    return db.query(Usuario).filter(Usuario.email == email).first()

# Para el login
def autenticar_usuario(db: Session, email: str, password: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return {"success": False, "message": "Usuario no encontrado."}
    if not verify_password(password, usuario.password):
        return {"success": False, "message": "Contraseña incorrecta."}
    if usuario.estadoCuenta != "activo":
        return {"success": False, "message": "Cuenta pendiente de activación."}
    
    return {"success": True, "message": "Inicio de sesión exitoso", "usuario": usuario}

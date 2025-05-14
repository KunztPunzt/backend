from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import logging
import traceback

from backend.repositorios.usuario import obtener_por_email
from backend.utilidades.config import settings
from backend.servicios.baseDatos import SessionLocal
from backend.utilidades.seguridad import decode_token

# Configurar logging
logger = logging.getLogger(__name__)

def get_db():
    """Proporciona una instancia de sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Define dónde se obtiene el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/token")

async def get_current_user(request: Request = None, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Obtiene el usuario actual a partir del token JWT.
    
    Args:
        request: Objeto de solicitud HTTP
        token: Token JWT de autenticación
        db: Sesión de base de datos
        
    Returns:
        Usuario actual autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    client_info = f"{request.client.host}:{request.client.port}" if request and request.client else "desconocido"
    logger.debug(f"Verificando autenticación para cliente: {client_info}")
    
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar token JWT
        logger.debug(f"Decodificando token JWT")
        payload = decode_token(token)
        
        # Extraer email del token
        email = payload.get("sub")
        if not email:
            logger.warning("Token JWT sin campo 'sub'")
            raise credentials_exc
        
        logger.debug(f"Token decodificado exitosamente para: {email}")
    except JWTError as e:
        logger.error(f"Error al decodificar token JWT: {str(e)}")
        raise credentials_exc
    except Exception as e:
        # Captura cualquier otra excepción durante la decodificación
        error_details = traceback.format_exc()
        logger.error(f"Error inesperado al decodificar token: {str(e)}\n{error_details}")
        raise credentials_exc
    
    # Buscar usuario en la base de datos
    try:
        user = obtener_por_email(db, email)
        if not user:
            logger.warning(f"Usuario no encontrado en base de datos: {email}")
            raise credentials_exc
        
        # Verificar estado de la cuenta
        if user.estadoCuenta != "activo":
            logger.warning(f"Intento de acceso con cuenta no activa: {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta no activa. Por favor active su cuenta primero.",
            )
        
        logger.debug(f"Usuario autenticado exitosamente: {email}")
        return user
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    except Exception as e:
        # Capturar cualquier otra excepción durante la consulta a la base de datos
        error_details = traceback.format_exc()
        logger.error(f"Error al consultar usuario en base de datos: {str(e)}\n{error_details}")
        raise credentials_exc
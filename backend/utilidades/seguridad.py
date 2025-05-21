# backend/utilidades/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from backend.utilidades.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Para obtener token de autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/token")

# bcrypt con coste moderado
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")

def hash_password(password: str) -> str:
    """Hashea una contraseña usando el algoritmo bcrypt"""
    try:
        hashed = pwd_context.hash(password)
        return hashed
    except Exception as e:
        logger.error(f"Error al hashear contraseña: {str(e)}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con su hash"""
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        return result
    except Exception as e:
        logger.error(f"Error al verificar contraseña: {str(e)}")
        return False

# Alias para compatibilidad con otros módulos
obtener_password_hash = hash_password
verificar_contrasena = verify_password

# JWT de acceso
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crea un token JWT con la información proporcionada.
    
    Args:
        data: Diccionario con los datos a incluir en el token
        expires_delta: Tiempo de expiración opcional
        
    Returns:
        Token JWT firmado
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Usar hours como indica el nombre de la variable
            expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        
        # Añadir tiempo de emisión y expiración
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow()
        })
        
        # Firmar el token con la clave secreta
        token = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.jwt_algorithm
        )
        
        logger.debug(f"Token creado correctamente para usuario: {data.get('sub', 'desconocido')}")
        return token
    except Exception as e:
        logger.error(f"Error al crear token JWT: {str(e)}")
        raise

def decode_token(token: str) -> dict:
    """
    Decodifica un token JWT y verifica su validez.
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Payload del token decodificado
        
    Raises:
        JWTError: Si el token no es válido o ha expirado
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        logger.error(f"Error al decodificar token JWT: {str(e)}")
        raise

async def obtenerUsuarioActual(token: str = Depends(oauth2_scheme)):
    """
    Obtiene el usuario actual basado en el token JWT proporcionado.
    Implementado en estilo CamelCase según las preferencias del proyecto.
    
    Args:
        token: Token JWT de autenticación
        
    Returns:
        dict: Información del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credencialesException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        usuarioId = payload.get("sub")
        if usuarioId is None:
            raise credencialesException
            
        # Aquí normalmente verificarías la existencia del usuario en la BD
        # Por ahora, simplemente devolvemos la información del token
        # Aseguramos que el rol devuelto esté en minúsculas, usando 'usuario' como default.
        return {
            "id": usuarioId,
            "rol": payload.get("rol", "usuario").lower(), 
            "email": payload.get("email", "")
        }
    except JWTError:
        raise credencialesException

# Alias para compatibilidad con snake_case
obtener_usuario_actual = obtenerUsuarioActual
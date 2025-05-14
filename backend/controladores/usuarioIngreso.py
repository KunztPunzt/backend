from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import traceback
from typing import Annotated

# Rutas de directorio
from backend.dtos.tokenDto import Token
from backend.repositorios.usuario import autenticar_usuario, obtener_por_email
from backend.utilidades.dependencias import get_db, get_current_user
from backend.utilidades.seguridad import create_access_token
import logging

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/token", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para autenticar al usuario y generar un token JWT.
    
    Args:
        form_data: Formulario de autenticación con username y password
        db: Sesión de base de datos
        
    Returns:
        Token de acceso y tipo de token
    """
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Intento de login desde {client_host} para usuario: {form_data.username}")
    
    try:
        # Verificar si el usuario existe en la base de datos
        usuario = obtener_por_email(db, form_data.username)
        if not usuario:
            logger.warning(f"Intento de login con usuario inexistente: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Autenticar usuario
        resultado = autenticar_usuario(db, form_data.username, form_data.password)
        if not resultado["success"]:
            logger.warning(f"Autenticación fallida para usuario {form_data.username}: {resultado['message']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=resultado["message"],
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar que la cuenta esté activa
        if usuario.estadoCuenta != "activo":
            logger.warning(f"Intento de login con cuenta no activa: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta no activa. Por favor active su cuenta primero.",
            )
        
        # Generar token JWT
        access_token = create_access_token({"sub": form_data.username})
        logger.info(f"Login exitoso para el usuario {form_data.username}")
        
        # Devolver token
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        # Re-lanzar excepciones HTTP para mantener sus códigos y mensajes
        raise
    except Exception as e:
        # Capturar todas las demás excepciones, loggearlas con detalles y devolver un 500
        error_details = traceback.format_exc()
        logger.error(f"Error inesperado en login para {form_data.username}: {str(e)}\n{error_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante la autenticación",
        )


@router.get("/perfil")
def leer_perfil(current_user=Depends(get_current_user)):
    """
    Devuelve la información del perfil del usuario autenticado.
    
    Args:
        current_user: Usuario actual obtenido del token JWT
        
    Returns:
        Información básica del perfil del usuario
    """
    try:
        return {
            "email": current_user.email,
            "nombre": current_user.nombre,
            "rol": current_user.rol
        }
    except Exception as e:
        logger.error(f"Error al obtener perfil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el perfil del usuario",
        )

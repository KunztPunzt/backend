# Importar librerias
from fastapi import BackgroundTasks, APIRouter, HTTPException, Query, Depends, Request
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi.responses import HTMLResponse, JSONResponse


# Llamada a dependecias del proyecto
from backend.dtos.usuarioRegistroDto import UsuarioCrear, UsuarioRespuesta
from backend.repositorios import usuario as repositorio_usuario
from backend.utilidades.dependencias import get_db
from backend.utilidades.enviarCorreo import send_activation_email
from backend.utilidades.config import settings
from backend.dtos.cambiarContrasenaDto import CambiarContrasenaDto
from fastapi import status
import logging

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Registro Usuario

@router.post("/registro", response_model=UsuarioRespuesta)
async def registrar_usuario(datos_usuario: UsuarioCrear, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    logger.info(f"Iniciando registro de usuario: {datos_usuario.email}")
    usuario_existente = repositorio_usuario.obtener_por_email(db, datos_usuario.email)
    if usuario_existente:
        logger.warning(f"Intento de registro con email ya existente: {datos_usuario.email}")
        raise HTTPException(status_code=400, detail="El correo ya está en uso")
    
    nuevo_usuario = repositorio_usuario.crear_usuario(db, datos_usuario)
    background_tasks.add_task(
        send_activation_email,
        nuevo_usuario.email,
        nuevo_usuario.tokenActivacion
    )
    logger.info(f"Usuario registrado correctamente: {datos_usuario.email}. Se ha enviado correo de activación.")
    return nuevo_usuario

@router.get("/activar")
def activar_cuenta(request: Request, token: str = Query(...), db: Session = Depends(get_db)):
    """
    Activa la cuenta de usuario mediante token de validación.
    Puede responder en formato JSON o HTML dependiendo del Accept header.
    """
    logger.debug(f"Procesando activación de cuenta con token")
    
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        email = payload.get("sub")
        if not email:
            logger.warning("Token sin campo 'sub'")
            return _generar_respuesta_error(request, "Token inválido o expirado", 400)
    except JWTError as e:
        logger.warning(f"Error al decodificar token de activación: {str(e)}")
        return _generar_respuesta_error(request, "Token inválido o expirado", 400)

    usuario = repositorio_usuario.obtener_por_email(db, email)
    if not usuario or usuario.tokenActivacion != token:
        logger.warning(f"Token de activación no coincide para email: {email}")
        return _generar_respuesta_error(request, "Token de activación no coincide", 400)
    
    usuario.estadoCuenta = "activo"
    usuario.tokenActivacion = None
    db.commit()
    logger.info(f"Cuenta activada correctamente para: {email}")
    
    # Verificar si el cliente acepta HTML o prefiere JSON
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        return HTMLResponse("""
            <html>
            <body style='text-align:center; margin-top:50px;'>
                <h2>¡Cuenta activada correctamente!</h2>
                <p>Ya puedes iniciar sesión en Yavanna.</p>
                <a href='/docs' style='color: #4CAF50; font-weight: bold;'>Ir a la aplicación</a>
            </body>
            </html>
        """)
    else:
        return {"mensaje": "Cuenta activada correctamente."}

def _generar_respuesta_error(request: Request, mensaje: str, codigo: int):
    """Helper para generar respuestas de error en formato HTML o JSON según el Accept header"""
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        return HTMLResponse(f"<h2>{mensaje}</h2>", status_code=codigo)
    else:
        return JSONResponse({"error": mensaje}, status_code=codigo)
    
    from fastapi import FastAPI, WebSocket



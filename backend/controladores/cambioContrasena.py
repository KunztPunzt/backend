from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend.dtos.cambiarContrasenaDto import CambiarContrasenaDto
from backend.utilidades.seguridad import verificar_contrasena, obtener_password_hash
from backend.utilidades.dependencias import get_db, get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post(
    "/cambiar-contrasena", 
    status_code=status.HTTP_200_OK,
    summary="Cambiar Contraseña de Usuario"
)
def cambiar_contrasena(datos: CambiarContrasenaDto, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Permite al usuario cambiar su contraseña actual por una nueva.
    
    - Valida que la contraseña actual sea correcta
    - Verifica que la nueva contraseña y su confirmación coincidan
    - Aplica requisitos de seguridad para la nueva contraseña
    - Actualiza la contraseña en la base de datos
    """
    # 1. Validar contraseña actual
    if not verificar_contrasena(datos.contrasenaActual, current_user.password):
        return HTMLResponse("<h3>La contraseña actual es incorrecta.</h3>", status_code=400)
    # 2. Validar coincidencia de nueva contraseña
    if datos.nuevaContrasena != datos.confirmarNuevaContrasena:
        return HTMLResponse("<h3>La nueva contraseña y la confirmación no coinciden.</h3>", status_code=400)
    # 3. Validar requisitos de seguridad (ejemplo: longitud mínima y combinación de caracteres)
    if len(datos.nuevaContrasena) < 8 or datos.nuevaContrasena.isdigit() or datos.nuevaContrasena.isalpha():
        return HTMLResponse("<h3>La nueva contraseña debe tener al menos 8 caracteres y combinar letras y números.</h3>", status_code=400)
    # 4. Actualizar contraseña
    current_user.password = obtener_password_hash(datos.nuevaContrasena)
    db.commit()
    return HTMLResponse("<h3>¡Contraseña cambiada exitosamente!</h3>") 
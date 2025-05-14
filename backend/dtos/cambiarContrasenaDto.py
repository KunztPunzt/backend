from pydantic import BaseModel, Field, validator
from backend.utilidades.validadores import validar_contraseña

class CambiarContrasenaDto(BaseModel):
    contrasenaActual: str = Field(..., min_length=6)
    nuevaContrasena: str = Field(..., min_length=8)
    confirmarNuevaContrasena: str = Field(..., min_length=8)

    @validator('nuevaContrasena')
    def validar_nueva_contrasena(cls, v):
        return validar_contraseña(v)

    @validator('confirmarNuevaContrasena')
    def validar_confirmacion_contrasena(cls, v, values):
        if 'nuevaContrasena' in values and v != values['nuevaContrasena']:
            raise ValueError('Las contraseñas no coinciden')
        return v 
from pydantic import BaseModel, EmailStr, Field, validator
from pydantic import ConfigDict
from typing import Optional
from backend.utilidades.validadores import validar_contraseña, validar_email_dominio

class UsuarioCrear(BaseModel):
    nombre: str = Field(..., max_length=100)
    apellidos: str = Field(..., max_length=100)
    email: EmailStr # Restaurado a EmailStr
    password: str = Field(..., min_length=8)
    rol: str = Field(default="cliente")
    estado_cuenta: str = Field(default="pendiente")
    token_activacion: Optional[str] = None

    @validator('email') # Descomentado
    def validar_email(cls, v):
        return validar_email_dominio(v)

    @validator('password')
    def validar_password(cls, v):
        return validar_contraseña(v)

class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_user: int = Field(...,alias="idUser")
    nombre: str
    apellidos: str
    email: EmailStr # Mantenemos EmailStr aquí para la respuesta, o cambiar a str si es necesario
    rol: str
    estado_cuenta: str = Field(..., alias="estadoCuenta")

import re
from typing import Optional
from pydantic import EmailStr, validator
from pydantic_core import PydanticCustomError

def validar_contraseña(contraseña: str) -> str:
    """
    Valida que la contraseña cumpla con los requisitos:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    if len(contraseña) < 8:
        raise PydanticCustomError(
            'contraseña_corta',
            'La contraseña debe tener al menos 8 caracteres'
        )
    
    if not re.search(r'[A-Z]', contraseña):
        raise PydanticCustomError(
            'sin_mayuscula',
            'La contraseña debe contener al menos una letra mayúscula'
        )
    
    if not re.search(r'[a-z]', contraseña):
        raise PydanticCustomError(
            'sin_minuscula',
            'La contraseña debe contener al menos una letra minúscula'
        )
    
    if not re.search(r'\d', contraseña):
        raise PydanticCustomError(
            'sin_numero',
            'La contraseña debe contener al menos un número'
        )
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contraseña):
        raise PydanticCustomError(
            'sin_caracter_especial',
            'La contraseña debe contener al menos un carácter especial'
        )
    
    return contraseña

def validar_email_dominio(email: EmailStr) -> EmailStr:
    """
    Valida que el dominio del email sea válido
    """
    dominio = email.split('@')[1]
    dominios_validos = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com']
    
    if dominio not in dominios_validos:
        raise PydanticCustomError(
            'dominio_invalido',
            'El dominio del correo electrónico no es válido'
        )
    
    return email 
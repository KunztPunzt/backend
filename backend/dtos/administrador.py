from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile

class AdministradorBase(BaseModel):
    nombre: str
    apellidos: str
    email: EmailStr
    rol: str = "admin"

class AdministradorCreate(AdministradorBase):
    password: str

class AdministradorUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    estadoCuenta: Optional[str] = None

class AdministradorResponse(AdministradorBase):
    id: int = Field(..., alias="idUser")
    estadoCuenta: str
    fechaCreacion: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class EstadisticasSistema(BaseModel):
    totalUsuarios: int
    totalVeterinarios: int
    totalMascotas: int
    totalCitas: int
    citasPendientes: int
    citasCompletadas: int
    citasCanceladas: int

class VeterinarioRegistro(BaseModel):
    # Datos de usuario
    nombre: constr(min_length=2, max_length=100)
    apellidos: constr(min_length=2, max_length=100)
    email: EmailStr
    password: constr(min_length=8)
    
    # Datos específicos del veterinario
    almaMater: constr(min_length=2, max_length=200)
    diploma: UploadFile
    añosExperiencia: int
    especialidad: constr(min_length=2, max_length=100) 
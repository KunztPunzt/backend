from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import List

from backend.servicios.baseDatos import get_db
from backend.servicios.administrador import ServicioAdministrador
from backend.dtos.administrador import (
    AdministradorCreate,
    EstadisticasSistema,
    VeterinarioRegistro
)
from backend.utilidades.seguridad import obtenerUsuarioActual

router = APIRouter(
    prefix="/admin",
    tags=["Administrador"]
)

@router.post(
    "/", 
    response_model=AdministradorCreate, 
    status_code=status.HTTP_201_CREATED, 
    name="Crear Nuevo Administrador",
    summary="Crear Nuevo Administrador"
)
def crearNuevoAdministrador(
    admin: AdministradorCreate,
    db: Session = Depends(get_db),
    usuarioActual: dict = Depends(obtenerUsuarioActual)
):
    """
    Crea un nuevo administrador en el sistema.
    Solo los administradores existentes pueden crear nuevos administradores.
    """
    if usuarioActual["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear administradores"
        )
    
    servicio = ServicioAdministrador(db)
    return servicio.crearAdministrador(admin)

@router.get(
    "/estadisticas", 
    response_model=EstadisticasSistema, 
    name="Obtener Estadísticas del Sistema",
    summary="Obtener Estadísticas del Sistema"
)
def obtenerEstadisticasSistema(
    db: Session = Depends(get_db),
    usuarioActual: dict = Depends(obtenerUsuarioActual)
):
    """
    Obtiene estadísticas generales del sistema.
    Solo los administradores pueden ver estas estadísticas.
    """
    if usuarioActual["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver estadísticas"
        )
    
    servicio = ServicioAdministrador(db)
    return servicio.getEstadisticas()

@router.post(
    "/veterinarios", 
    status_code=status.HTTP_201_CREATED, 
    name="Registrar Nuevo Veterinario",
    summary="Registrar Nuevo Veterinario"
)
def registrarNuevoVeterinario(
    nombre: str = Form(...),
    apellidos: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    almaMater: str = Form(...),
    diploma: UploadFile = File(...),
    añosExperiencia: int = Form(...),
    especialidad: str = Form(...),
    db: Session = Depends(get_db),
    usuarioActual: dict = Depends(obtenerUsuarioActual)
):
    """
    Registra un nuevo veterinario en el sistema.
    
    - Solo los administradores pueden registrar nuevos veterinarios
    - Se requiere cargar un archivo como diploma
    - El sistema envía un correo de activación al veterinario registrado
    """
    if usuarioActual["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para registrar veterinarios"
        )
    
    servicio = ServicioAdministrador(db)
    usuario = servicio.registrarVeterinario(
        nombre=nombre,
        apellidos=apellidos,
        email=email,
        password=password,
        almaMater=almaMater,
        diploma=diploma,
        añosExperiencia=añosExperiencia,
        especialidad=especialidad
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    return {
        "mensaje": "Veterinario registrado exitosamente",
        "tokenActivacion": usuario.tokenActivacion
    } 
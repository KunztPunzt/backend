from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.servicios.baseDatos import get_db
from backend.servicios.administrador import ServicioAdministrador
from backend.dtos.administrador import (
    AdministradorCreate,
    EstadisticasSistema,
    VeterinarioRegistro
)
from backend.utilidades.seguridad import obtenerUsuarioActual
from backend.utilidades.enviarCorreo import send_activation_email

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
    background_tasks: BackgroundTasks = BackgroundTasks(),
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
    
    # Enviar correo de activación
    background_tasks.add_task(
        send_activation_email,
        usuario.email,
        usuario.tokenActivacion
    )
    
    return {
        "mensaje": "Veterinario registrado exitosamente. Se ha enviado un correo de activación.",
        "email": usuario.email
    }

@router.put(
    "/veterinarios/{veterinario_id}/validar-diploma",
    status_code=status.HTTP_200_OK,
    name="Validar Diploma de Veterinario",
    summary="Validar Diploma de Veterinario"
)
def validarDiplomaVeterinario(
    veterinario_id: int,
    es_valido: bool = Form(...),
    observaciones: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    usuarioActual: dict = Depends(obtenerUsuarioActual)
):
    """
    Valida el diploma de un veterinario.
    
    - Solo los administradores pueden validar diplomas
    - Se puede aprobar o rechazar el diploma
    - Se pueden agregar observaciones opcionales
    - Al aprobar el diploma, se activa la cuenta del veterinario
    """
    if usuarioActual["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para validar diplomas"
        )
    
    servicio = ServicioAdministrador(db)
    veterinario = servicio.validarDiplomaVeterinario(
        veterinario_id=veterinario_id,
        es_valido=es_valido,
        observaciones=observaciones
    )
    
    return {
        "mensaje": "Diploma validado exitosamente",
        "estado": veterinario.estadoLicencia,
        "observaciones": veterinario.observacionesDiploma
    }

@router.post(
    "/asistentes", 
    status_code=status.HTTP_201_CREATED, 
    name="Registrar Nuevo Asistente",
    summary="Registrar Nuevo Asistente"
)
def registrarNuevoAsistente(
    nombre: str = Form(...),
    apellidos: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    usuarioActual: dict = Depends(obtenerUsuarioActual)
):
    """
    Registra un nuevo asistente en el sistema.
    
    - Solo los administradores pueden registrar nuevos asistentes
    - El sistema envía un correo de activación al asistente registrado
    """
    if usuarioActual["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para registrar asistentes"
        )
    
    servicio = ServicioAdministrador(db)
    usuario = servicio.registrarAsistente(
        nombre=nombre,
        apellidos=apellidos,
        email=email,
        password=password
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Enviar correo de activación
    background_tasks.add_task(
        send_activation_email,
        usuario.email,
        usuario.tokenActivacion
    )
    
    return {
        "mensaje": "Asistente registrado exitosamente. Se ha enviado un correo de activación.",
        "email": usuario.email
    } 
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.servicios.baseDatos import get_db
from backend.servicios.auditoria import ServicioAuditoria
from backend.modelos.auditoria import Auditoria
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

router = APIRouter()

class AuditoriaResponse(BaseModel):
    id: int
    tabla: str
    accion: str
    usuario_id: Optional[int]
    fecha: datetime
    datos_anteriores: Optional[Dict[str, Any]]
    datos_nuevos: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    detalles: Optional[str]

    class Config:
        from_attributes = True

@router.get("/auditoria", response_model=List[AuditoriaResponse])
async def obtener_registros_auditoria(
    tabla: Optional[str] = Query(None, description="Filtrar por nombre de tabla"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    accion: Optional[str] = Query(None, description="Filtrar por tipo de acción (INSERT, UPDATE, DELETE)"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    offset: int = Query(0, description="Número de registros a saltar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene registros de auditoría con filtros opcionales.
    Solo usuarios con rol 'admin' pueden acceder a estos registros.
    """
    # TODO: Implementar verificación de rol de administrador
    
    registros = ServicioAuditoria.obtener_registros(
        db=db,
        tabla=tabla,
        usuario_id=usuario_id,
        accion=accion,
        limit=limit,
        offset=offset
    )
    
    return registros

@router.get("/auditoria/{id}", response_model=AuditoriaResponse)
async def obtener_registro_auditoria(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un registro específico de auditoría por su ID.
    Solo usuarios con rol 'admin' pueden acceder a estos registros.
    """
    # TODO: Implementar verificación de rol de administrador
    
    registro = db.query(Auditoria).filter(Auditoria.id == id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de auditoría no encontrado")
    
    return registro 
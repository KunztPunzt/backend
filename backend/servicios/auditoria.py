from sqlalchemy.orm import Session
from fastapi import Request
from backend.modelos.auditoria import Auditoria
from typing import Optional, Dict, Any
import json
from datetime import datetime

class ServicioAuditoria:
    @staticmethod
    def registrar_cambio(
        db: Session,
        request: Request,
        tabla: str,
        accion: str,
        usuario_id: int,
        datos_anteriores: Optional[Dict[str, Any]] = None,
        datos_nuevos: Optional[Dict[str, Any]] = None,
        detalles: Optional[str] = None
    ) -> Auditoria:
        """
        Registra un cambio en el sistema de auditoría.
        
        Args:
            db: Sesión de base de datos
            request: Objeto Request de FastAPI
            tabla: Nombre de la tabla afectada
            accion: Tipo de acción (INSERT, UPDATE, DELETE)
            usuario_id: ID del usuario que realizó la acción
            datos_anteriores: Datos antes del cambio (opcional)
            datos_nuevos: Datos después del cambio (opcional)
            detalles: Información adicional sobre el cambio (opcional)
            
        Returns:
            Registro de auditoría creado
        """
        # Obtener IP del cliente
        ip_address = request.client.host if request.client else None
        
        # Crear registro de auditoría
        registro_auditoria = Auditoria(
            tabla=tabla,
            accion=accion,
            usuarioId=usuario_id,
            fecha=datetime.utcnow(),
            datosAnteriores=datos_anteriores,
            datosNuevos=datos_nuevos,
            ipAddress=ip_address,
            detalles=detalles
        )
        
        db.add(registro_auditoria)
        db.commit()
        db.refresh(registro_auditoria)
        
        return registro_auditoria

    @staticmethod
    def obtener_registros(
        db: Session,
        tabla: Optional[str] = None,
        usuario_id: Optional[int] = None,
        accion: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Auditoria]:
        """
        Obtiene registros de auditoría con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            tabla: Filtrar por nombre de tabla
            usuario_id: Filtrar por ID de usuario
            accion: Filtrar por tipo de acción
            limit: Límite de registros a retornar
            offset: Número de registros a saltar
            
        Returns:
            Lista de registros de auditoría
        """
        query = db.query(Auditoria)
        
        if tabla:
            query = query.filter(Auditoria.tabla == tabla)
        if usuario_id:
            query = query.filter(Auditoria.usuarioId == usuario_id)
        if accion:
            query = query.filter(Auditoria.accion == accion)
            
        return query.order_by(Auditoria.fecha.desc()).offset(offset).limit(limit).all() 
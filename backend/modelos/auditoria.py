from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.servicios.baseDatos import Base

class Auditoria(Base):
    __tablename__ = "Auditoria"

    id = Column(Integer, primary_key=True, index=True)
    tabla = Column(String(100), nullable=False)
    accion = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    usuarioId = Column(Integer, ForeignKey("Usuario.idUser"), nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    datosAnteriores = Column(JSON, nullable=True)
    datosNuevos = Column(JSON, nullable=True)
    ipAddress = Column(String(50), nullable=True)
    detalles = Column(String(500), nullable=True)

    # Relación con usuario
    usuario = relationship("Usuario", back_populates="auditorias") 
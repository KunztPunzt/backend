from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.mssql import NVARCHAR, DECIMAL
from sqlalchemy.orm import relationship

from backend.servicios.baseDatos import Base

class Cita(Base):
    __tablename__ = "Cita"

    idCita = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("Usuario.idUser"), nullable=False)
    idVeterinario = Column(Integer, ForeignKey("Veterinario.idVeterinario"), nullable=True)
    idServicio = Column(Integer, ForeignKey("Servicio.idServicio"), nullable=False)
    idMascota = Column(Integer, ForeignKey("Mascota.idMascota"), nullable=False)
    fechaHora = Column(DateTime, nullable=False)
    fotoAnimal = Column(NVARCHAR(255), nullable=True)
    notasAdicionales = Column(NVARCHAR(500), nullable=True)
    estado = Column(NVARCHAR(20), nullable=False, default="pendiente")
    recordatorioEnviado = Column(Boolean, nullable=False, default=False)
    motivoCancelacion = Column(NVARCHAR(500), nullable=True)
    diagnostico = Column(NVARCHAR(1000), nullable=True)
    peso = Column(DECIMAL(5, 2), nullable=True)
    

    # Relaciones ORM
    usuario = relationship("Usuario", back_populates="citas")
    veterinario = relationship("Veterinario", back_populates="citas")
    servicio = relationship("Servicio", back_populates="citas")
    mascota = relationship("Mascota", back_populates="citas")
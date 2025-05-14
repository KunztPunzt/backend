from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.servicios.baseDatos import Base
from sqlalchemy.dialects.mssql import NVARCHAR

class Veterinario(Base):
    __tablename__ = "Veterinario"
    idVeterinario = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("Usuario.idUser"), nullable=False)    
    almaMater = Column(NVARCHAR(200),nullable=False)
    diploma = Column(NVARCHAR(255),nullable=False)
    añosExperiencia = Column(Integer, nullable=False)
    especialidad = Column(NVARCHAR(100),nullable=False)
    estadoLicencia = Column(NVARCHAR(50),nullable=False)
    
    servicios = relationship(
        "VeterinarioServicio",
        back_populates="veterinario",
        cascade="all, delete-orphan"
    )

    usuario = relationship("Usuario", back_populates="veterinario")
    citas = relationship("Cita",back_populates="veterinario")


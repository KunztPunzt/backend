from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mssql import NVARCHAR, DECIMAL
from sqlalchemy.orm import relationship
from backend.servicios.baseDatos import Base

class Servicio(Base):
    __tablename__ = "Servicio"

    idServicio = Column(Integer, primary_key=True, index=True)
    nombre = Column(NVARCHAR(100), nullable=False)
    descripcion = Column(NVARCHAR(500), nullable=True)
    precio = Column(DECIMAL(10, 2), nullable=False)
    duracionMin = Column(Integer, nullable=False)
    
    veterinarios = relationship(
        "VeterinarioServicio",
        back_populates="servicio",
        cascade="all, delete-orphan"
    )

    # Relación con citas (cuando se implemente Cita)
    citas = relationship("Cita", back_populates="servicio")
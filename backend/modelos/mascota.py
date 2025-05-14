from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.servicios.baseDatos import Base
from sqlalchemy.dialects.mssql import NVARCHAR

class Mascota(Base):
    __tablename__ = "Mascota"

    idMascota = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("Usuario.idUser"), nullable=False)
    nombre = Column(NVARCHAR(100), nullable=False)
    especie = Column(NVARCHAR(50), nullable=False)
    raza = Column(NVARCHAR(100), nullable=False)
    edad = Column(Integer, nullable=True)
    fechaNacimiento = Column(Date, nullable=True)
    foto = Column(NVARCHAR(255), nullable=True)
    notas = Column(NVARCHAR(500), nullable=True)

    # relación hacia Usuario    
    usuario = relationship("Usuario", back_populates="mascotas", uselist=False)
    citas = relationship(
    "Cita",back_populates="mascota")


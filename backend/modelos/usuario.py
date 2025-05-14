from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from backend.servicios.baseDatos import Base
from sqlalchemy.dialects.mssql import NVARCHAR

class Usuario(Base):
    __tablename__ = "Usuario"
    
    idUser = Column(Integer, primary_key=True, index=True)
    nombre = Column(NVARCHAR(100), nullable=False)
    apellidos = Column(NVARCHAR(100), nullable=False)
    email = Column(NVARCHAR(255), unique=True, nullable=False, index=True)
    password = Column(NVARCHAR(255), nullable=False)
    rol = Column(NVARCHAR(50), nullable=False)
    estadoCuenta = Column(NVARCHAR(50), nullable=False)
    tokenActivacion = Column(NVARCHAR(255), nullable=True)
    # relación hacia Mascota
    mascotas = relationship("Mascota", back_populates="usuario", cascade="all, delete-orphan")
    veterinario = relationship("Veterinario", back_populates="usuario", cascade="all, delete-orphan", uselist=False)
    citas = relationship("Cita",back_populates="usuario", cascade="all, delete-orphan")


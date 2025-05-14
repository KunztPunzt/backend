from sqlalchemy import (Column, Integer, DECIMAL, ForeignKey)
from backend.servicios.baseDatos import Base
from sqlalchemy.orm import relationship


class VeterinarioServicio(Base):
    __tablename__ = "VeterinarioServicio"

    id = Column(Integer, primary_key=True)
    veterinarioId = Column(
        Integer,
        ForeignKey("Veterinario.idVeterinario", ondelete="CASCADE"),
        nullable=False
    )
    servicioId = Column(
        Integer,
        ForeignKey("Servicio.idServicio", ondelete="CASCADE"),
        nullable=False
    )
    precioEspecial = Column(DECIMAL(10, 2), nullable=True)
    duracionMin = Column(Integer, nullable=True)

    # Relaciones inversas
    veterinario = relationship(
        "Veterinario",
        back_populates="servicios",

    )
    servicio = relationship(
        "Servicio",
        back_populates="veterinarios",

    )

    

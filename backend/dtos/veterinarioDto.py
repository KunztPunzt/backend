from pydantic import BaseModel
from typing import Optional

class VeterinarioDto(BaseModel):
    idVeterinario: int
    nombre: str
    especialidad: str
    añosExperiencia: int
    estadoLicencia: str
    almaMater: str

    class Config:
        from_attributes = True 
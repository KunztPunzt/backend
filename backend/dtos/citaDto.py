from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
from decimal import Decimal


class TipoServicio(str, Enum):
    CONSULTA_VETERINARIA = "Consulta veterinaria"
    VACUNACION = "Vacunación"
    TRATAMIENTO_CIRUGIA = "Tratamiento y cirugía"
    CONTROL = "Control"
    PET_GROOMING = "Pet grooming"


# Dato de entrada para el POST, con el idMascota elegido por el cliente, el servicio, fecha y hora.
class CitaCrearDto(BaseModel):
    idMascota: int
    tipoServicio: TipoServicio
    fechaHora: datetime
    notasAdicionales: Optional[str] = None
    idVeterinario: int

# DTO para actualizar una cita existente
class CitaActualizarDto(BaseModel):
    fechaHora: Optional[datetime] = None
    tipoServicio: Optional[TipoServicio] = None
    notasAdicionales: Optional[str] = None
    idVeterinario: Optional[int] = None
    diagnostico: Optional[str] = None
    peso: Optional[Decimal] = None

# Para la respuesta, incluye el ID generado y el estado (pendiente, confirmada, atendida…).

class CitaDto(BaseModel):
    idCita: int
    idMascota: int
    tipoServicio: TipoServicio
    fechaHora: datetime
    notasAdicionales: Optional[str] = None
    estado: str
    motivoCancelacion: Optional[str] = None
    diagnostico: Optional[str] = None
    peso: Optional[Decimal] = None

# DTO para cancelar una cita con motivo
class CitaCancelarDto(BaseModel):
    motivoCancelacion: str


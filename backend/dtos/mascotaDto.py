from pydantic import BaseModel
from datetime import date
from typing import Optional

class MascotaCrearDto(BaseModel):
    nombre: str
    especie: str
    raza: str
    edad: Optional[int] = None
    fechaNacimiento: Optional[date] = None
    notas: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "nombre": "Firulais",
                "especie": "Perro",
                "raza": "Labrador",
                "edad": 3,
                "fechaNacimiento": "2021-06-15",
                "notas": "Muy juguetón"
            }
        }

class MascotaDto(BaseModel):
    idMascota:   int
    nombre:      str
    especie:     str
    raza:        str
    edad:        Optional[int]   = None
    fechaNacimiento: Optional[date] = None
    notas:       Optional[str]   = None
    foto:        str             

    class Config:
        from_attributes = True  
        schema_extra = {
            "example": {
                "idMascota": 1,
                "nombre": "Firulais",
                "especie": "Perro",
                "raza": "Labrador",
                "edad": 3,
                "fechaNacimiento": "2021-06-15",
                "notas": "Muy juguetón",
                "foto": "/static/mascotas/firulais.jpg"
            }
        }

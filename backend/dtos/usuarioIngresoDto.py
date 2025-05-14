from pydantic import BaseModel, EmailStr

class IngresoDto(BaseModel):
    email: EmailStr
    password: str

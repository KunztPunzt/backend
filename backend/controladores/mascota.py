# backend/controladores/mascota.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import uuid
import os
import shutil
from datetime import date
from typing import List

from backend.dtos.mascotaDto import MascotaCrearDto, MascotaDto
from backend.modelos.mascota import Mascota
from backend.utilidades.dependencias import get_db, get_current_user

router = APIRouter(prefix="/mascotas", tags=["Mascotas"])

@router.post("/", response_model=MascotaDto, status_code=status.HTTP_201_CREATED)
def subir_mascota(
    nombre: str = Form(...),
    especie: str = Form(...),
    raza: str = Form(...),
    edad: int | None = Form(None),
    fechaNacimiento: date | None = Form(None),
    notas: str | None = Form(None),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Permite a un usuario con rol 'cliente' subir una nueva mascota junto con su foto.
    """
    # Validar que el usuario sea cliente
    if current_user.rol != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo usuarios con rol 'cliente' pueden subir mascotas."
        )

    # Generar nombre único para la foto
    extension = os.path.splitext(foto.filename)[1]
    nombre_archivo = f"{uuid.uuid4().hex}{extension}"
    carpeta = os.path.join("static", "mascotas")
    os.makedirs(carpeta, exist_ok=True)
    ruta_archivo = os.path.join(carpeta, nombre_archivo)

    # Guardar archivo en disco
    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    # Construir URL de la foto para almacenar en la base de datos
    foto_url = f"/static/mascotas/{nombre_archivo}"

    # Crear instancia ORM de Mascota
    nueva_mascota = Mascota(
        nombre=nombre,
        especie=especie,
        raza=raza,
        edad=edad,
        fechaNacimiento=fechaNacimiento,
        notas=notas,
        foto=foto_url,
        idUsuario=current_user.idUser
    )
    db.add(nueva_mascota)
    db.commit()
    db.refresh(nueva_mascota)

    return nueva_mascota

@router.get("/mis-mascotas", response_model=List[MascotaDto])
def listar_mis_mascotas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Obtiene la lista de mascotas registradas por el usuario actual.
    Solo usuarios con rol 'cliente' pueden acceder a sus mascotas.
    """
    if current_user.rol != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo usuarios con rol 'cliente' pueden ver sus mascotas."
        )
    
    mascotas = db.query(Mascota).filter(Mascota.idUsuario == current_user.idUser).all()
    return mascotas

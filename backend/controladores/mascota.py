# backend/controladores/mascota.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from sqlalchemy.orm import Session
import uuid
import os
import shutil
from datetime import date
from typing import List

from backend.dtos.mascotaDto import MascotaCrearDto, MascotaDto
from backend.modelos.mascota import Mascota
from backend.utilidades.dependencias import get_db, get_current_user
from backend.servicios.auditoria import ServicioAuditoria

router = APIRouter(prefix="/mascotas", tags=["Mascotas"])

@router.post("/", response_model=MascotaDto, status_code=status.HTTP_201_CREATED)
def subir_mascota(
    request: Request,
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

    # Registrar en auditoría
    datos_nuevos = {
        "idMascota": nueva_mascota.idMascota,
        "nombre": nombre,
        "especie": especie,
        "raza": raza,
        "edad": edad,
        "fechaNacimiento": str(fechaNacimiento) if fechaNacimiento else None,
        "notas": notas,
        "foto": foto_url,
        "idUsuario": current_user.idUser
    }
    
    ServicioAuditoria.registrar_cambio(
        db=db,
        request=request,
        tabla="Mascota",
        accion="INSERT",
        usuario_id=current_user.idUser,
        datos_nuevos=datos_nuevos,
        detalles=f"Nueva mascota '{nombre}' registrada"
    )

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

@router.put("/{mascota_id}", response_model=MascotaDto)
def actualizar_mascota(
    request: Request,
    mascota_id: int,
    nombre: str = Form(...),
    especie: str = Form(...),
    raza: str = Form(...),
    edad: int | None = Form(None),
    fechaNacimiento: date | None = Form(None),
    notas: str | None = Form(None),
    foto: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Permite actualizar los datos de una mascota existente.
    """
    # Validar que el usuario sea cliente
    if current_user.rol != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo usuarios con rol 'cliente' pueden actualizar mascotas."
        )

    # Buscar la mascota
    mascota = db.query(Mascota).filter(
        Mascota.idMascota == mascota_id,
        Mascota.idUsuario == current_user.idUser
    ).first()

    if not mascota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )

    # Guardar datos anteriores para auditoría
    datos_anteriores = {
        "idMascota": mascota.idMascota,
        "nombre": mascota.nombre,
        "especie": mascota.especie,
        "raza": mascota.raza,
        "edad": mascota.edad,
        "fechaNacimiento": str(mascota.fechaNacimiento) if mascota.fechaNacimiento else None,
        "notas": mascota.notas,
        "foto": mascota.foto,
        "idUsuario": mascota.idUsuario
    }

    # Actualizar datos
    mascota.nombre = nombre
    mascota.especie = especie
    mascota.raza = raza
    mascota.edad = edad
    mascota.fechaNacimiento = fechaNacimiento
    mascota.notas = notas

    # Si se proporciona una nueva foto
    if foto:
        # Eliminar foto anterior si existe
        if mascota.foto:
            ruta_foto_anterior = os.path.join("static", mascota.foto.lstrip("/"))
            if os.path.exists(ruta_foto_anterior):
                os.remove(ruta_foto_anterior)

        # Guardar nueva foto
        extension = os.path.splitext(foto.filename)[1]
        nombre_archivo = f"{uuid.uuid4().hex}{extension}"
        carpeta = os.path.join("static", "mascotas")
        os.makedirs(carpeta, exist_ok=True)
        ruta_archivo = os.path.join(carpeta, nombre_archivo)

        with open(ruta_archivo, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

        mascota.foto = f"/static/mascotas/{nombre_archivo}"

    db.commit()
    db.refresh(mascota)

    # Registrar en auditoría
    datos_nuevos = {
        "idMascota": mascota.idMascota,
        "nombre": nombre,
        "especie": especie,
        "raza": raza,
        "edad": edad,
        "fechaNacimiento": str(fechaNacimiento) if fechaNacimiento else None,
        "notas": notas,
        "foto": mascota.foto,
        "idUsuario": mascota.idUsuario
    }

    ServicioAuditoria.registrar_cambio(
        db=db,
        request=request,
        tabla="Mascota",
        accion="UPDATE",
        usuario_id=current_user.idUser,
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos,
        detalles=f"Actualización de mascota '{nombre}'"
    )

    return mascota

@router.delete("/{mascota_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mascota(
    request: Request,
    mascota_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Permite a un usuario con rol 'cliente' eliminar una de sus mascotas.
    """
    # Validar que el usuario sea cliente
    if current_user.rol != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo usuarios con rol 'cliente' pueden eliminar mascotas."
        )

    # Buscar la mascota asegurando que pertenezca al usuario actual
    mascota = db.query(Mascota).filter(
        Mascota.idMascota == mascota_id,
        Mascota.idUsuario == current_user.idUser
    ).first()

    if not mascota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada o no pertenece al usuario actual"
        )

    # Guardar datos para auditoría
    datos_eliminados = {
        "idMascota": mascota.idMascota,
        "nombre": mascota.nombre,
        "especie": mascota.especie,
        "raza": mascota.raza,
        "edad": mascota.edad,
        "fechaNacimiento": str(mascota.fechaNacimiento) if mascota.fechaNacimiento else None,
        "notas": mascota.notas,
        "foto": mascota.foto,
        "idUsuario": mascota.idUsuario
    }

    # Eliminar foto si existe
    if mascota.foto:
        ruta_foto = os.path.join("static", mascota.foto.lstrip("/"))
        if os.path.exists(ruta_foto):
            try:
                os.remove(ruta_foto)
            except Exception as e:
                # Registrar error pero continuar con la eliminación
                print(f"Error al eliminar archivo: {str(e)}")

    # Eliminar mascota de la base de datos
    db.delete(mascota)
    db.commit()

    # Registrar en auditoría
    ServicioAuditoria.registrar_cambio(
        db=db,
        request=request,
        tabla="Mascota",
        accion="DELETE",
        usuario_id=current_user.idUser,
        datos_anteriores=datos_eliminados,
        detalles=f"Eliminación de mascota '{mascota.nombre}'"
    )

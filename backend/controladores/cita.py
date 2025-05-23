from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.dtos.citaDto import CitaCrearDto, CitaDto, TipoServicio, CitaActualizarDto, CitaCancelarDto
from backend.dtos.veterinarioDto import VeterinarioDto
from backend.modelos.cita import Cita
from backend.modelos.mascota import Mascota
from backend.modelos.servicio import Servicio
from backend.modelos.veterinario import Veterinario
from backend.utilidades.dependencias import get_db, get_current_user
from typing import List
from decimal import Decimal

router = APIRouter(prefix="/citas", tags=["Citas"])

@router.post(
    "/", 
    response_model=CitaDto, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear Nueva Cita"
)
def crear_cita(
    cita_in: CitaCrearDto,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Crea una nueva cita para una mascota.
    
    - Solo usuarios con rol 'cliente' pueden crear citas
    - La mascota debe pertenecer al cliente
    - El servicio debe existir en el sistema
    - El veterinario, si se especifica, debe existir
    """
    # 1) Sólo clientes
    if current_user.rol != "cliente":
        raise HTTPException(403, "Solo clientes pueden solicitar citas.")

    # 2) Mascota válida y propia
    mascota = db.get(Mascota, cita_in.idMascota)
    if not mascota or mascota.idUsuario != current_user.idUser:
        raise HTTPException(404, "Mascota no encontrada o no te pertenece.")

    # 3) Servicio válido (buscar por nombre)
    servicio = db.query(Servicio).filter(Servicio.nombre == cita_in.tipoServicio.value).first()
    if not servicio:
        raise HTTPException(404, "Servicio no encontrado.")

    # 4) Validar veterinario si se proporciona
    id_veterinario = cita_in.idVeterinario
    veterinario = None
    if id_veterinario is not None:
        veterinario = db.get(Veterinario, id_veterinario)
        if not veterinario:
            raise HTTPException(404, "Veterinario no encontrado.")

    # 5) Crear la cita
    nueva = Cita(
        idMascota = cita_in.idMascota,
        idServicio = servicio.idServicio,
        fechaHora = cita_in.fechaHora,
        notasAdicionales = cita_in.notasAdicionales,
        estado = "pendiente",
        idUsuario = current_user.idUser,
        idVeterinario = id_veterinario
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    servicio = db.get(Servicio, nueva.idServicio)
    tipo_servicio = TipoServicio(servicio.nombre)
    return CitaDto(
        idCita=nueva.idCita,
        idMascota=nueva.idMascota,
        tipoServicio=tipo_servicio,
        fechaHora=nueva.fechaHora,
        notasAdicionales=nueva.notasAdicionales,
        estado=nueva.estado,
        motivoCancelacion=nueva.motivoCancelacion,
        diagnostico=nueva.diagnostico,
        peso=nueva.peso
    )

@router.put(
    "/{idCita}", 
    response_model=CitaDto,
    summary="Modificar Cita Existente"
)
def modificar_cita(
    idCita: int,
    cita_update: CitaActualizarDto,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Modifica una cita existente.
    
    - Solo el cliente propietario puede modificar sus citas
    - Se pueden modificar: fecha/hora, tipo de servicio, notas y veterinario
    """
    # Buscar la cita
    cita = db.get(Cita, idCita)
    if not cita:
        raise HTTPException(404, "Cita no encontrada.")

    # Solo el cliente dueño puede modificar
    if current_user.rol != "cliente" or cita.idUsuario != current_user.idUser:
        raise HTTPException(403, "No tienes permiso para modificar esta cita.")

    # Actualizar campos permitidos
    if cita_update.fechaHora is not None:
        cita.fechaHora = cita_update.fechaHora
    if cita_update.tipoServicio is not None:
        servicio = db.query(Servicio).filter(Servicio.nombre == cita_update.tipoServicio.value).first()
        if not servicio:
            raise HTTPException(404, "Servicio no encontrado.")
        cita.idServicio = servicio.idServicio
    if cita_update.notasAdicionales is not None:
        cita.notasAdicionales = cita_update.notasAdicionales
    if cita_update.idVeterinario is not None:
        veterinario = db.get(Veterinario, cita_update.idVeterinario)
        if not veterinario:
            raise HTTPException(404, "Veterinario no encontrado.")
        cita.idVeterinario = cita_update.idVeterinario

    db.commit()
    db.refresh(cita)

    # Obtener el tipo de servicio actualizado
    servicio = db.get(Servicio, cita.idServicio)
    tipo_servicio = TipoServicio(servicio.nombre)

    return CitaDto(
        idCita=cita.idCita,
        idMascota=cita.idMascota,
        tipoServicio=tipo_servicio,
        fechaHora=cita.fechaHora,
        notasAdicionales=cita.notasAdicionales,
        estado=cita.estado,
        motivoCancelacion=cita.motivoCancelacion,
        diagnostico=cita.diagnostico,
        peso=cita.peso
    )

@router.delete(
    "/{idCita}", 
    response_model=CitaDto,
    summary="Cancelar Cita"
)
def cancelar_cita(
    idCita: int,
    cancelacion: CitaCancelarDto,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Cancela una cita existente.
    
    - Solo el cliente propietario puede cancelar sus citas
    - Se requiere indicar un motivo de cancelación
    """
    cita = db.get(Cita, idCita)
    if not cita:
        raise HTTPException(404, "Cita no encontrada.")
    if current_user.rol != "cliente" or cita.idUsuario != current_user.idUser:
        raise HTTPException(403, "No tienes permiso para cancelar esta cita.")
    cita.estado = "cancelada"
    cita.motivoCancelacion = cancelacion.motivoCancelacion
    db.commit()
    db.refresh(cita)
    servicio = db.get(Servicio, cita.idServicio)
    tipo_servicio = TipoServicio(servicio.nombre)
    return CitaDto(
        idCita=cita.idCita,
        idMascota=cita.idMascota,
        tipoServicio=tipo_servicio,
        fechaHora=cita.fechaHora,
        notasAdicionales=cita.notasAdicionales,
        estado=cita.estado,
        motivoCancelacion=cita.motivoCancelacion,
        diagnostico=cita.diagnostico,
        peso=cita.peso
    )

@router.put(
    "/{idCita}/confirmar", 
    response_model=CitaDto,
    summary="Confirmar Asistencia a Cita"
)
def confirmar_cita(
    idCita: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Confirma la asistencia a una cita pendiente.
    
    - Solo el cliente propietario puede confirmar sus citas
    - Solo se pueden confirmar citas en estado 'pendiente'
    """
    cita = db.get(Cita, idCita)
    if not cita:
        raise HTTPException(404, "Cita no encontrada.")
    if current_user.rol != "cliente" or cita.idUsuario != current_user.idUser:
        raise HTTPException(403, "No tienes permiso para confirmar esta cita.")
    if cita.estado != "pendiente":
        raise HTTPException(400, "Solo se pueden confirmar citas pendientes.")
    cita.estado = "confirmada"
    db.commit()
    db.refresh(cita)
    servicio = db.get(Servicio, cita.idServicio)
    tipo_servicio = TipoServicio(servicio.nombre)
    return CitaDto(
        idCita=cita.idCita,
        idMascota=cita.idMascota,
        tipoServicio=tipo_servicio,
        fechaHora=cita.fechaHora,
        notasAdicionales=cita.notasAdicionales,
        estado=cita.estado,
        motivoCancelacion=cita.motivoCancelacion,
        diagnostico=cita.diagnostico,
        peso=cita.peso
    )

@router.get(
    "/veterinarios", 
    response_model=List[VeterinarioDto],
    summary="Listar Veterinarios Disponibles"
)
def obtener_veterinarios_disponibles(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Obtiene la lista de todos los veterinarios disponibles en el sistema.
    
    - Disponible para todos los usuarios autenticados
    - Incluye nombre completo, especialidad y experiencia de cada veterinario
    """
    veterinarios = db.query(Veterinario).all()
    
    # Transformar los resultados para incluir el nombre del usuario
    veterinarios_dto = []
    for vet in veterinarios:
        veterinarios_dto.append(
            VeterinarioDto(
                idVeterinario=vet.idVeterinario,
                nombre=f"{vet.usuario.nombre} {vet.usuario.apellidos}",
                especialidad=vet.especialidad,
                añosExperiencia=vet.añosExperiencia,
                estadoLicencia=vet.estadoLicencia,
                almaMater=vet.almaMater
            )
        )
    
    return veterinarios_dto

@router.put(
    "/{idCita}/atender", 
    response_model=CitaDto,
    summary="Atender Cita"
)
def atender_cita(
    idCita: int,
    diagnostico: str,
    peso: Decimal,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Atiende una cita y registra el diagnóstico y peso de la mascota.
    
    - Solo veterinarios pueden atender citas
    - La cita debe estar en estado 'confirmada'
    - Se registra el diagnóstico y peso de la mascota
    - La cita pasa a estado 'completada'
    """
    # Verificar que el usuario sea veterinario
    if current_user.rol != "veterinario":
        raise HTTPException(403, "Solo veterinarios pueden atender citas.")

    # Buscar la cita
    cita = db.get(Cita, idCita)
    if not cita:
        raise HTTPException(404, "Cita no encontrada.")

    # Verificar que la cita esté confirmada
    if cita.estado != "confirmada":
        raise HTTPException(400, "Solo se pueden atender citas confirmadas.")

    # Actualizar la cita
    cita.diagnostico = diagnostico
    cita.peso = peso
    cita.estado = "completada"

    db.commit()
    db.refresh(cita)

    # Obtener el tipo de servicio
    servicio = db.get(Servicio, cita.idServicio)
    tipo_servicio = TipoServicio(servicio.nombre)

    return CitaDto(
        idCita=cita.idCita,
        idMascota=cita.idMascota,
        tipoServicio=tipo_servicio,
        fechaHora=cita.fechaHora,
        notasAdicionales=cita.notasAdicionales,
        estado=cita.estado,
        motivoCancelacion=cita.motivoCancelacion,
        diagnostico=cita.diagnostico,
        peso=cita.peso
    )

@router.get(
    "/historial/{idMascota}",
    response_model=List[CitaDto],
    summary="Historial médico de una mascota"
)
def historial_medico(
    idMascota: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Devuelve el historial médico de una mascota (solo citas completadas), ordenadas por fecha descendente.
    - El dueño de la mascota, veterinarios y admins pueden consultar el historial.
    """
    # Verificar que la mascota exista
    mascota = db.get(Mascota, idMascota)
    if not mascota:
        raise HTTPException(404, "Mascota no encontrada.")

    # Permitir solo al dueño, veterinario o admin
    if not (
        (current_user.rol == "cliente" and mascota.idUsuario == current_user.idUser)
        or current_user.rol in ["veterinario", "admin"]
    ):
        raise HTTPException(403, "No tienes permiso para ver el historial de esta mascota.")

    # Consultar citas completadas
    citas = (
        db.query(Cita)
        .filter(Cita.idMascota == idMascota, Cita.estado == "completada")
        .order_by(Cita.fechaHora.desc())
        .all()
    )

    resultado = []
    for cita in citas:
        servicio = db.get(Servicio, cita.idServicio)
        tipo_servicio = TipoServicio(servicio.nombre)
        resultado.append(CitaDto(
            idCita=cita.idCita,
            idMascota=cita.idMascota,
            tipoServicio=tipo_servicio,
            fechaHora=cita.fechaHora,
            notasAdicionales=cita.notasAdicionales,
            estado=cita.estado,
            motivoCancelacion=cita.motivoCancelacion,
            diagnostico=cita.diagnostico,
            peso=cita.peso
        ))
    return resultado

@router.get(
    "/",
    response_model=List[CitaDto],
    summary="Listar Todas las Citas"
)
def listar_citas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Lista todas las citas del sistema.
    
    - Clientes: ven solo sus propias citas
    - Veterinarios: ven todas las citas
    - Asistentes: ven todas las citas
    """
    # Filtrar citas según el rol del usuario
    if current_user.rol == "cliente":
        citas = db.query(Cita).filter(Cita.idUsuario == current_user.idUser).all()
    else:
        citas = db.query(Cita).all()

    resultado = []
    for cita in citas:
        servicio = db.get(Servicio, cita.idServicio)
        tipo_servicio = TipoServicio(servicio.nombre)
        resultado.append(CitaDto(
            idCita=cita.idCita,
            idMascota=cita.idMascota,
            tipoServicio=tipo_servicio,
            fechaHora=cita.fechaHora,
            notasAdicionales=cita.notasAdicionales,
            estado=cita.estado,
            motivoCancelacion=cita.motivoCancelacion,
            diagnostico=cita.diagnostico,
            peso=cita.peso
        ))
    return resultado


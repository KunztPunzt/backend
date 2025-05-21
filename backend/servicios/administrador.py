from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
import secrets
import os
import uuid
import shutil
from fastapi import UploadFile, HTTPException, status
from datetime import datetime, timedelta
import jwt
from fastapi import BackgroundTasks

from backend.modelos.usuario import Usuario
from backend.modelos.veterinario import Veterinario
from backend.modelos.mascota import Mascota
from backend.modelos.cita import Cita
from backend.dtos.administrador import (
    EstadisticasSistema, 
    AdministradorCreate, 
    AdministradorUpdate,
    AdministradorResponse,
    UsuarioUpdate,
    UsuarioResponse
)
from backend.utilidades.seguridad import hash_password
from backend.utilidades.enviarCorreo import send_activation_email
from backend.utilidades.config import settings

class ServicioAdministrador:
    def __init__(self, db: Session):
        self.db = db

    def getEstadisticas(self) -> EstadisticasSistema:
        total_usuarios = self.db.query(func.count(Usuario.idUser)).scalar()
        total_veterinarios = self.db.query(func.count(Veterinario.idVeterinario)).scalar()
        total_mascotas = self.db.query(func.count(Mascota.idMascota)).scalar()
        total_citas = self.db.query(func.count(Cita.idCita)).scalar()
        
        citas_pendientes = self.db.query(func.count(Cita.idCita)).filter(
            Cita.estado == "pendiente"
        ).scalar()
        
        citas_completadas = self.db.query(func.count(Cita.idCita)).filter(
            Cita.estado == "completada"
        ).scalar()
        
        citas_canceladas = self.db.query(func.count(Cita.idCita)).filter(
            Cita.estado == "cancelada"
        ).scalar()

        return EstadisticasSistema(
            totalUsuarios=total_usuarios,
            totalVeterinarios=total_veterinarios,
            totalMascotas=total_mascotas,
            totalCitas=total_citas,
            citasPendientes=citas_pendientes,
            citasCompletadas=citas_completadas,
            citasCanceladas=citas_canceladas
        )

    def crearAdministrador(self, admin: AdministradorCreate) -> AdministradorResponse:
        """
        Crea un nuevo administrador en el sistema.
        
        Args:
            admin: Datos del administrador a crear
            
        Returns:
            Información del administrador creado
        """
        # Verificar si el email ya existe
        if self.db.query(Usuario).filter(Usuario.email == admin.email).first():
            raise ValueError("El email ya está registrado")
            
        # Crear el usuario administrador
        nuevoAdmin = Usuario(
            nombre=admin.nombre,
            apellidos=admin.apellidos,
            email=admin.email,
            password=hash_password(admin.password),
            rol="admin",
            estadoCuenta="activo",
            tokenActivacion=None
        )
        
        self.db.add(nuevoAdmin)
        self.db.commit()
        self.db.refresh(nuevoAdmin)
        
        # Convertir a respuesta DTO
        return AdministradorResponse(
            id=nuevoAdmin.idUser,
            nombre=nuevoAdmin.nombre,
            apellidos=nuevoAdmin.apellidos,
            email=nuevoAdmin.email,
            rol=nuevoAdmin.rol,
            estadoCuenta=nuevoAdmin.estadoCuenta,
            fechaCreacion=nuevoAdmin.fechaCreacion
        )
        
    def obtenerAdministrador(self, admin_id: int) -> Optional[AdministradorResponse]:
        """
        Obtiene la información de un administrador por su ID.
        
        Args:
            admin_id: ID del administrador a buscar
            
        Returns:
            Información del administrador o None si no existe
        """
        adminDb = self.db.query(Usuario).filter(
            Usuario.idUser == admin_id,
            Usuario.rol == "admin"
        ).first()
        
        if not adminDb:
            return None
            
        return AdministradorResponse(
            id=adminDb.idUser,
            nombre=adminDb.nombre,
            apellidos=adminDb.apellidos,
            email=adminDb.email,
            rol=adminDb.rol,
            estadoCuenta=adminDb.estadoCuenta,
            fechaCreacion=adminDb.fechaCreacion
        )
        
    def actualizarAdministrador(
        self, 
        admin_id: int, 
        admin: AdministradorUpdate
    ) -> Optional[AdministradorResponse]:
        """
        Actualiza la información de un administrador existente.
        
        Args:
            admin_id: ID del administrador a actualizar
            admin: Datos nuevos del administrador
            
        Returns:
            Información actualizada del administrador o None si no existe
        """
        adminDb = self.db.query(Usuario).filter(
            Usuario.idUser == admin_id,
            Usuario.rol == "admin"
        ).first()
        
        if not adminDb:
            return None
            
        # Actualizar solo los campos proporcionados
        if admin.nombre is not None:
            adminDb.nombre = admin.nombre
            
        if admin.apellidos is not None:
            adminDb.apellidos = admin.apellidos
            
        if admin.email is not None:
            # Verificar que el email no esté en uso por otro usuario
            existeEmail = self.db.query(Usuario).filter(
                Usuario.email == admin.email,
                Usuario.idUser != admin_id
            ).first()
            
            if existeEmail:
                raise ValueError("El email ya está en uso por otro usuario")
                
            adminDb.email = admin.email
            
        if admin.password is not None:
            adminDb.password = hash_password(admin.password)
            
        if admin.estadoCuenta is not None:
            adminDb.estadoCuenta = admin.estadoCuenta.lower() # Asegurar minúsculas
            
        self.db.commit()
        self.db.refresh(adminDb)
        
        return AdministradorResponse(
            id=adminDb.idUser,
            nombre=adminDb.nombre,
            apellidos=adminDb.apellidos,
            email=adminDb.email,
            rol=adminDb.rol,
            estadoCuenta=adminDb.estadoCuenta,
            fechaCreacion=adminDb.fechaCreacion
        )

    def registrarVeterinario(
        self,
        nombre: str,
        apellidos: str,
        email: str,
        password: str,
        almaMater: str,
        diploma: UploadFile,
        añosExperiencia: int,
        especialidad: str
    ) -> Optional[Usuario]:
        # Verificar si el email ya existe
        if self.db.query(Usuario).filter(Usuario.email == email).first():
            return None

        # Guardar el archivo del diploma
        extension = os.path.splitext(diploma.filename)[1]
        nombre_archivo = f"{uuid.uuid4().hex}{extension}"
        carpeta = os.path.join("static", "documentos", "diplomas")
        os.makedirs(carpeta, exist_ok=True)
        ruta_archivo = os.path.join(carpeta, nombre_archivo)
        
        # Guardar archivo en disco
        with open(ruta_archivo, "wb") as buffer:
            shutil.copyfileobj(diploma.file, buffer)
        
        # URL para la base de datos
        url_diploma = f"/static/documentos/diplomas/{nombre_archivo}"

        # Generar token JWT con expiración
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        token = jwt.encode(
            {"sub": email, "exp": expire},
            settings.secret_key,
            algorithm=settings.jwt_algorithm
        )

        # Crear usuario veterinario
        db_usuario = Usuario(
            nombre=nombre,
            apellidos=apellidos,
            email=email,
            password=hash_password(password),
            rol="veterinario",
            estadoCuenta="pendiente",
            tokenActivacion=token
        )
        self.db.add(db_usuario)
        self.db.flush()  # Para obtener el ID del usuario

        # Crear registro de veterinario
        db_veterinario = Veterinario(
            idUsuario=db_usuario.idUser,
            almaMater=almaMater,
            diploma=url_diploma,  # Guardar URL del diploma
            añosExperiencia=añosExperiencia,
            especialidad=especialidad,
            estadoLicencia="pendiente"
        )
        self.db.add(db_veterinario)
        self.db.commit()
        self.db.refresh(db_usuario)

        # Enviar correo de activación
        background_tasks = BackgroundTasks()
        background_tasks.add_task(
            send_activation_email,
            db_usuario.email,
            db_usuario.tokenActivacion
        )

        return db_usuario 

    def validarDiplomaVeterinario(
        self,
        veterinario_id: int,
        es_valido: bool,
        observaciones: Optional[str] = None
    ) -> Veterinario:
        """
        Valida el diploma de un veterinario.
        
        Args:
            veterinario_id: ID del veterinario
            es_valido: True si el diploma es válido, False si no lo es
            observaciones: Observaciones opcionales sobre la validación
            
        Returns:
            Información actualizada del veterinario
        """
        veterinario = self.db.query(Veterinario).filter(
            Veterinario.idVeterinario == veterinario_id
        ).first()
        
        if not veterinario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )
            
        # Actualizar estado de la licencia
        veterinario.estadoLicencia = "aprobada" if es_valido else "rechazada"
        veterinario.observacionesDiploma = observaciones
        veterinario.fechaValidacion = datetime.utcnow()
        
        # Si el diploma es válido, activar la cuenta del veterinario
        if es_valido:
            usuario = self.db.query(Usuario).filter(
                Usuario.idUser == veterinario.idUsuario
            ).first()
            if usuario:
                usuario.estadoCuenta = "activo"
                usuario.tokenActivacion = None
        
        self.db.commit()
        self.db.refresh(veterinario)
        
        return veterinario 

    def registrarAsistente(
        self,
        nombre: str,
        apellidos: str,
        email: str,
        password: str
    ) -> Optional[Usuario]:
        """
        Registra un nuevo asistente en el sistema.
        
        Args:
            nombre: Nombre del asistente
            apellidos: Apellidos del asistente
            email: Email del asistente
            password: Contraseña del asistente
            
        Returns:
            Usuario creado o None si el email ya existe
        """
        # Verificar si el email ya existe
        if self.db.query(Usuario).filter(Usuario.email == email).first():
            return None

        # Generar token JWT con expiración
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        token = jwt.encode(
            {"sub": email, "exp": expire},
            settings.secret_key,
            algorithm=settings.jwt_algorithm
        )

        # Crear usuario asistente
        db_usuario = Usuario(
            nombre=nombre,
            apellidos=apellidos,
            email=email,
            password=hash_password(password),
            rol="asistente",
            estadoCuenta="pendiente",
            tokenActivacion=token
        )
        
        self.db.add(db_usuario)
        self.db.commit()
        self.db.refresh(db_usuario)

        # Enviar correo de activación
        background_tasks = BackgroundTasks()
        background_tasks.add_task(
            send_activation_email,
            db_usuario.email,
            db_usuario.tokenActivacion
        )

        return db_usuario 

    def listarUsuarios(self, skip: int = 0, limit: int = 100) -> List[UsuarioResponse]:
        """
        Lista todos los usuarios del sistema.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de usuarios
        """
        usuarios = self.db.query(Usuario).offset(skip).limit(limit).all()
        return [
            UsuarioResponse(
                id=usuario.idUser,
                nombre=usuario.nombre,
                apellidos=usuario.apellidos,
                email=usuario.email,
                rol=usuario.rol,
                estadoCuenta=usuario.estadoCuenta,
                fechaCreacion=usuario.fechaCreacion
            )
            for usuario in usuarios
        ]

    def eliminarUsuario(self, usuario_id: int) -> bool:
        """
        Elimina un usuario del sistema.
        
        Args:
            usuario_id: ID del usuario a eliminar
            
        Returns:
            True si el usuario fue eliminado, False si no existe
        """
        usuario = self.db.query(Usuario).filter(Usuario.idUser == usuario_id).first()
        if not usuario:
            return False
            
        # Si es un veterinario, eliminar también su registro
        if usuario.rol == "veterinario":
            veterinario = self.db.query(Veterinario).filter(
                Veterinario.idUsuario == usuario_id
            ).first()
            if veterinario:
                # Eliminar el archivo del diploma si existe
                if veterinario.diploma:
                    ruta_diploma = os.path.join("static", veterinario.diploma.lstrip("/"))
                    if os.path.exists(ruta_diploma):
                        os.remove(ruta_diploma)
                self.db.delete(veterinario)
        
        self.db.delete(usuario)
        self.db.commit()
        return True

    def modificarUsuario(
        self, 
        usuario_id: int, 
        usuario: UsuarioUpdate
    ) -> Optional[UsuarioResponse]:
        """
        Modifica la información de un usuario.
        
        Args:
            usuario_id: ID del usuario a modificar
            usuario: Datos nuevos del usuario
            
        Returns:
            Información actualizada del usuario o None si no existe
        """
        db_usuario = self.db.query(Usuario).filter(Usuario.idUser == usuario_id).first()
        if not db_usuario:
            return None
            
        # Actualizar solo los campos proporcionados
        if usuario.nombre is not None:
            db_usuario.nombre = usuario.nombre
            
        if usuario.apellidos is not None:
            db_usuario.apellidos = usuario.apellidos
            
        if usuario.email is not None:
            # Verificar que el email no esté en uso por otro usuario
            existe_email = self.db.query(Usuario).filter(
                Usuario.email == usuario.email,
                Usuario.idUser != usuario_id
            ).first()
            
            if existe_email:
                raise ValueError("El email ya está en uso por otro usuario")
                
            db_usuario.email = usuario.email
            
        if usuario.password is not None:
            db_usuario.password = hash_password(usuario.password)
            
        if usuario.rol is not None:
            db_usuario.rol = usuario.rol.lower()
            
        if usuario.estadoCuenta is not None:
            db_usuario.estadoCuenta = usuario.estadoCuenta.lower()
            
        self.db.commit()
        self.db.refresh(db_usuario)
        
        return UsuarioResponse(
            id=db_usuario.idUser,
            nombre=db_usuario.nombre,
            apellidos=db_usuario.apellidos,
            email=db_usuario.email,
            rol=db_usuario.rol,
            estadoCuenta=db_usuario.estadoCuenta,
            fechaCreacion=db_usuario.fechaCreacion
        ) 
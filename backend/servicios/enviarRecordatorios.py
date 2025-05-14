import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.modelos.cita import Cita
from backend.modelos.mascota import Mascota
from backend.modelos.servicio import Servicio
from backend.modelos.usuario import Usuario
from backend.utilidades.enviarCorreo import send_reminder_email
from backend.servicios.baseDatos import DATABASE_URL

# Crear sesión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def obtener_citas_para_recordatorio(db):
    ahora = datetime.utcnow()
    en_un_minuto = ahora + timedelta(minutes=1)
    print(f"[DEBUG] Buscando citas entre {ahora} y {en_un_minuto}")

    # Log de todas las citas pendientes
    pendientes = db.query(Cita).filter(Cita.estado == "pendiente", Cita.recordatorioEnviado == False).all()
    print(f"[DEBUG] Todas las citas pendientes:")
    for c in pendientes:
        print(f"[DEBUG] Cita id={c.idCita}, fechaHora={c.fechaHora}, usuario={c.idUsuario}")

    citas = db.query(Cita).filter(
        Cita.fechaHora >= ahora,
        Cita.fechaHora < en_un_minuto,
        Cita.estado == "pendiente",
        Cita.recordatorioEnviado == False
    ).all()
    print(f"[DEBUG] Citas encontradas: {len(citas)}")
    for c in citas:
        print(f"[DEBUG] Cita id={c.idCita}, usuario={c.idUsuario}, fechaHora={c.fechaHora}, recordatorioEnviado={c.recordatorioEnviado}")
    return citas

async def enviar_recordatorios():
    db = SessionLocal()
    citas = obtener_citas_para_recordatorio(db)
    for cita in citas:
        usuario = db.query(Usuario).filter(Usuario.idUser == cita.idUsuario).first()
        mascota = db.query(Mascota).filter(Mascota.idMascota == cita.idMascota).first()
        servicio = db.query(Servicio).filter(Servicio.idServicio == cita.idServicio).first()
        print(f"[DEBUG] Procesando cita {cita.idCita} para usuario {usuario.email if usuario else 'N/A'}")
        if usuario and mascota and servicio:
            fecha = cita.fechaHora.strftime('%d/%m/%Y')
            hora = cita.fechaHora.strftime('%H:%M')
            print(f"[DEBUG] Enviando recordatorio a {usuario.email} para la cita {cita.idCita}")
            await send_reminder_email(
                email=usuario.email,
                nombre_cliente=usuario.nombre,
                fecha=fecha,
                hora=hora,
                servicio=servicio.nombre,
                mascota=mascota.nombre,
                cita_id=cita.idCita
            )
            cita.recordatorioEnviado = True
            db.commit()
            print(f"[DEBUG] Recordatorio enviado a {usuario.email} para la cita {cita.idCita}")
        else:
            print(f"[DEBUG] Datos incompletos para la cita {cita.idCita}. No se envía recordatorio.")
    db.close()

if __name__ == "__main__":
    asyncio.run(enviar_recordatorios()) 
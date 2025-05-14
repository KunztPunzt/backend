from sqlalchemy.orm import Session
from backend.modelos.servicio import Servicio
from backend.servicios.baseDatos import SessionLocal

def init_servicios():
    db = SessionLocal()
    try:
        # Verificar si ya existen servicios
        if db.query(Servicio).first():
            print("Los servicios ya están inicializados")
            return

        # Crear los servicios básicos
        servicios = [
            Servicio(
                nombre="Consulta veterinaria",
                descripcion="Consulta general con el veterinario",
                precio=50.00,
                duracionMin=30
            ),
            Servicio(
                nombre="Vacunación",
                descripcion="Aplicación de vacunas",
                precio=35.00,
                duracionMin=20
            ),
            Servicio(
                nombre="Tratamiento y cirugía",
                descripcion="Procedimientos médicos y quirúrgicos",
                precio=150.00,
                duracionMin=60
            ),
            Servicio(
                nombre="Control",
                descripcion="Control y seguimiento de mascotas",
                precio=25.00,
                duracionMin=15
            ),
            Servicio(
                nombre="Pet grooming",
                descripcion="Cuidado estético para mascotas",
                precio=40.00,
                duracionMin=45
            )
        ]

        # Agregar todos los servicios
        for servicio in servicios:
            db.add(servicio)
        
        db.commit()
        print("Servicios inicializados correctamente")
    except Exception as e:
        print(f"Error al inicializar servicios: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_servicios() 
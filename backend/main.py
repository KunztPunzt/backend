from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from backend.servicios.enviarRecordatorios import enviar_recordatorios
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Importar los controladores
from backend.controladores import usuarioRegistro, usuarioIngreso
from backend.controladores.mascota import router as mascota_router
from backend.controladores.cita import router as cita_router
from backend.controladores.cambioContrasena import router as cambio_contrasena_router
from backend.controladores.auditoria import router as auditoria_router
from backend.controladores.administrador import router as administrador_router

# Conexión a la BD y creación de tablas
from backend.servicios.baseDatos import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Yavanna - API de Gestión Veterinaria",
    description="API para la gestión de clínica veterinaria Yavanna",
    version="1.0.0",
    # Personalizar apariencia de Swagger UI
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Oculta esquemas por defecto
        "deepLinking": True,             # Permitir links directos a operaciones
        "displayRequestDuration": True,  # Muestra duración de la petición
        "docExpansion": "list"           # Operaciones colapsadas por defecto
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, se debe limitar a los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],
)

# Montar carpeta de archivos estáticos (para fotos de mascotas)
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

@app.on_event("startup")
def start_scheduler():
    logger.info("Iniciando aplicación y configurando scheduler")
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(enviar_recordatorios()), 'interval', minutes=5)
    scheduler.start()
    logger.info("Scheduler configurado correctamente")

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Routers de usuario - usar los tags definidos en cada router
app.include_router(usuarioRegistro.router, prefix="/usuarios")
app.include_router(usuarioIngreso.router, prefix="/usuarios")

# Router de mascotas
app.include_router(mascota_router, prefix="/mascotas")

# Router Citas
app.include_router(cita_router, prefix="/citas")

# Router de cambio de contraseña
app.include_router(cambio_contrasena_router)

# Router de auditoría
app.include_router(auditoria_router, prefix="/admin")

# Router de administrador
app.include_router(administrador_router)

logger.info("Aplicación configurada y lista para recibir peticiones")

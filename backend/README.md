# Yavanna - Backend

Backend de la aplicación Yavanna, un sistema de gestión veterinaria desarrollado con FastAPI.

## Requisitos

- Python 3.8+
- SQL Server Management Studio (SSMS) para la base de datos
- Acceso a un servidor SQL Server

## Dependencias principales

| Paquete                | ¿Para qué sirve?                                        |
|------------------------|---------------------------------------------------------|
| `fastapi`              | Framework para construir el backend                     |
| `uvicorn[standard]`    | Servidor para correr FastAPI                            |
| `pydantic`             | Validación de datos y creación de esquemas              |
| `pydantic-settings`    | Manejo de configuración basada en entorno               |
| `email-validator`      | Validar correos electrónicos                            |
| `sqlalchemy`           | ORM similar a Entity Framework                          |
| `pyodbc`               | Driver para conectarnos a SQL Server                    |
| `python-dotenv`        | Leer variables desde `.env`                             |
| `python-jose`          | Para generar y verificar JWTs                           |
| `passlib[bcrypt]`      | Para encriptar contraseñas de forma segura              |
| `python-multipart`     | Procesar formularios multipart en FastAPI               |
| `alembic`              | Gestionar migraciones de base de datos                  |
| `apscheduler`          | Tareas programadas y recordatorios                      |
| `fastapi-mail`         | Envío de correos electrónicos                           |
| `pydantic_core`        | Errores personalizados y validaciones avanzadas         |

## Instalación y primer uso

1. **Clona el repositorio y navega a la carpeta backend:**

```bash
git clone [URL_DEL_REPOSITORIO]
cd backend
```

2. **Configura las variables de entorno:**

Crea un archivo `.env` en la raíz de `backend` con las siguientes variables (ajusta según tu entorno):

```
DATABASE_URL=mssql+pyodbc://usuario:contraseña@servidor/nombre_bd?driver=ODBC+Driver+17+for+SQL+Server
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAIL_USERNAME=tu_correo@example.com
MAIL_PASSWORD=tu_contraseña
MAIL_FROM=tu_correo@example.com
MAIL_SERVER=smtp.tuservidor.com
MAIL_FROM_NAME=Yavanna
MAIL_PORT=587
```
3. **Ejecuta el script de configuración (Windows, PowerShell):**
Para ello se debe navegar hasta la carpeta `/backend`

```
./setup.ps1
```

Esto creará el entorno virtual, instalará las dependencias y dejará todo listo.

4. **Ejecuta las migraciones de la base de datos:**

```bash
alembic upgrade head
```

5. **Inicia el servidor:**

```bash
uvicorn main:app --reload
```

## Estructura del Proyecto

```
backend/
├── alembic/              # Migraciones de base de datos
├── controladores/        # Endpoints de la API (usuarios, mascotas, citas, etc.)
├── dtos/                 # Modelos de datos para validación y transferencia
├── modelos/              # Modelos de SQLAlchemy (tablas)
├── repositorios/         # Lógica de acceso a datos
├── servicios/            # Lógica de negocio y utilidades de base de datos
├── utilidades/           # Helpers, validadores, seguridad, envío de correos
├── static/               # Archivos estáticos (imágenes de mascotas, etc.)
├── main.py               # Punto de entrada de la aplicación
├── setup.ps1             # Script de configuración automática
└── .env                  # Variables de entorno (no subir a repositorios públicos)
```

## Características principales

- Autenticación JWT
- Gestión de usuarios y roles
- Gestión de mascotas
- Sistema de citas
- Recordatorios automáticos por correo
- Manejo de archivos estáticos
- Envío de correos electrónicos (activación, recordatorios, etc.)
- Migraciones automáticas con Alembic
- Tareas programadas con APScheduler

## API Endpoints principales

- `/usuarios` - Gestión de usuarios
- `/mascotas` - Gestión de mascotas
- `/citas` - Gestión de citas
- `/usuarios/cambiar-contrasena` - Cambio de contraseña

## Documentación interactiva

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notas y recomendaciones

- **No subas el archivo `.env` a repositorios públicos.**
- El proyecto está preparado para trabajar con SQL Server (SSMS) usando `pyodbc`.
---

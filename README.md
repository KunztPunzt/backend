# Yavanna

Sistema de gestión y control de mascotas desarrollado con FastAPI.

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

## Instalación

1. **Clonar el repositorio:**
```bash
git clone [URL_DEL_REPOSITORIO]
cd Yavanna
```

2. **Configurar las variables de entorno:**
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
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

3. **Ejecutar el script de configuración (Windows, PowerShell):**
```powershell
cd backend
./setup.ps1
```

4. **Ejecutar migraciones:**
```bash
alembic upgrade head
```

5. **Iniciar el servidor:**
```bash
uvicorn backend.main:app --reload
```

## Estructura del Proyecto

```
Yavanna/
├── backend/             # Código fuente del backend
│   ├── alembic/        # Migraciones de base de datos
│   ├── controladores/  # Endpoints de la API
│   ├── dtos/          # Modelos de datos para validación
│   ├── modelos/       # Modelos de SQLAlchemy
│   ├── repositorios/  # Lógica de acceso a datos
│   ├── servicios/     # Lógica de negocio
│   ├── utilidades/    # Helpers y utilidades
│   ├── static/        # Archivos estáticos
│   └── main.py        # Punto de entrada
├── frontend/          # Código fuente del frontend
└── logs/             # Archivos de registro
```

## Características principales

- Autenticación JWT
- Gestión de usuarios y roles
- Gestión de mascotas
- Sistema de citas
- Recordatorios automáticos por correo
- Manejo de archivos estáticos
- Envío de correos electrónicos
- Migraciones automáticas con Alembic
- Tareas programadas con APScheduler

## API Endpoints principales

- `/usuarios` - Gestión de usuarios
- `/mascotas` - Gestión de mascotas
- `/citas` - Gestión de citas
- `/usuarios/cambiar-contrasena` - Cambio de contraseña

## Documentación API

La documentación de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notas y recomendaciones

- **No subas el archivo `.env` a repositorios públicos.**
- El proyecto está preparado para trabajar con SQL Server (SSMS) usando `pyodbc`.
- Asegúrate de tener instalado el driver ODBC para SQL Server. 
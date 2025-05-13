# Yavanna

Sistema de gestión y control de mascotas desarrollado con FastAPI.

## Requisitos

- Python 3.8+
- PostgreSQL (o la base de datos configurada en el proyecto)

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd Yavanna
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
DATABASE_URL=tu_url_de_base_de_datos
SECRET_KEY=tu_clave_secreta
```

5. Ejecutar migraciones:
```bash
alembic upgrade head
```

6. Iniciar el servidor:
```bash
uvicorn backend.main:app --reload
```

## Estructura del Proyecto

- `backend/`: Código fuente del backend
  - `controladores/`: Endpoints de la API
  - `dtos/`: Objetos de transferencia de datos
  - `repositorios/`: Lógica de acceso a datos
  - `utilidades/`: Funciones y utilidades comunes
- `frontend/`: Código fuente del frontend
- `alembic/`: Migraciones de base de datos

## Documentación API

La documentación de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 
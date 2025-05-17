from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import backend.modelos.usuario    # define Usuario
import backend.modelos.mascota     # define Mascota
import backend.modelos.veterinario # define Veterinario
import backend.modelos.cita        # define Cita
import backend.modelos.servicio    # define Servicio
import backend.modelos.veterinarioServicio 
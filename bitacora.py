from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configuración de la base de datos SQLite
DATABASE_URL = "sqlite:///./bitacora.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Inicializar la aplicación FastAPI
app = FastAPI()

# Modelo para la tabla "log_access"
class LogAccess(Base):
    __tablename__ = "log_access"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_url = Column(String, nullable=False)  # URL de la imagen (cadena de texto)
    date = Column(String, nullable=False)  # Fecha en formato de cadena

# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo para registrar acceso en la bitácora
class LogAccessCreate(BaseModel):
    image_url: str  # URL de la imagen
    date: str  # Fecha en formato de cadena

# Endpoint para registrar un intento de acceso en la bitácora
@app.post("/log/")
def create_log_entry(log_data: LogAccessCreate, db: Session = Depends(get_db)):
    log_entry = LogAccess(image_url=log_data.image_url, date=log_data.date)
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry

# Endpoint para obtener todos los registros de la bitácora
@app.get("/log/")
def get_log_entries(db: Session = Depends(get_db)):
    logs = db.query(LogAccess).all()
    return logs

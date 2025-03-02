from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import datetime

# Conectar con MongoDB
MONGO_URL = "mongodb://localhost:27017"  # Cambia esto si usas MongoDB Atlas
DATABASE_NAME = "bitacora_db"
COLLECTION_NAME = "log_access"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Inicializar FastAPI
app = FastAPI()

# Modelo de datos para la bitácora
class LogAccessCreate(BaseModel):
    image_url: str  # URL de la imagen
    date: str  # Fecha en formato de cadena (YYYY-MM-DD HH:MM:SS)

# ✅ Endpoint para registrar un intento de acceso en la bitácora
@app.post("/log/")
async def create_log_entry(log_data: LogAccessCreate):
    log_entry = {
        "image_url": log_data.image_url,
        "date": log_data.date
    }
    result = await collection.insert_one(log_entry)
    return {"id": str(result.inserted_id), **log_entry}

# ✅ Endpoint para obtener todos los registros de la bitácora
@app.get("/log/")
async def get_log_entries():
    logs = await collection.find().to_list(None)
    for log in logs:
        log["_id"] = str(log["_id"])  # Convertir ObjectId a string
    return logs

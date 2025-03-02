from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# 🔹 Conexión con MongoDB
MONGO_URL = "mongodb://localhost:27017"  # Cambia esto si usas MongoDB Atlas
DATABASE_NAME = "users_db"
COLLECTION_NAME = "users"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# 🔹 Inicializar FastAPI
app = FastAPI()

# 🔹 Modelo para la creación y actualización de usuario
class UserBase(BaseModel):
    name: str  # Nombre del usuario
    image_path: str  # URL de la imagen

# ✅ **1. Crear un usuario**
@app.post("/users/")
async def create_user(user_data: UserBase):
    user = {
        "name": user_data.name,
        "image_path": user_data.image_path,
        "is_active": True  # Todos los usuarios comienzan activos
    }
    result = await collection.insert_one(user)
    return {"id": str(result.inserted_id), **user}

# ✅ **2. Actualizar un usuario**
@app.put("/users/{user_id}")
async def update_user(user_id: str, user_data: UserBase):
    result = await collection.update_one(
        {"_id": ObjectId(user_id), "is_active": True},  # Buscar solo usuarios activos
        {"$set": {"name": user_data.name, "image_path": user_data.image_path}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario actualizado"}

# ✅ **3. Eliminar un usuario (eliminación lógica)**
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario eliminado (lógicamente)"}

# ✅ **4. Obtener usuarios activos**
@app.get("/users/")
async def get_users():
    users = await collection.find({"is_active": True}).to_list(None)
    for user in users:
        user["_id"] = str(user["_id"])  # Convertir ObjectId a string
    
    return users

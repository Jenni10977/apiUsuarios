from fastapi import FastAPI, HTTPException, Depends  # Importamos FastAPI y las herramientas necesarias
from pydantic import BaseModel  # Importamos BaseModel para la validación de datos
from sqlalchemy import create_engine, Column, Integer, String, Boolean  # Importamos SQLAlchemy para manejar la base de datos
from sqlalchemy.ext.declarative import declarative_base  # Base para la creación de modelos
from sqlalchemy.orm import sessionmaker, Session  # Manejo de sesiones en SQLAlchemy

# Configuración de la base de datos SQLite
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # Conectamos a la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Configuración de la sesión de base de datos
Base = declarative_base()  # Base para definir los modelos

# Inicializamos la aplicación FastAPI
app = FastAPI()

# Definimos el modelo de la base de datos para la tabla "users"
class User(Base):
    __tablename__ = "users"  # Nombre de la tabla en la base de datos
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # ID autoincremental
    name = Column(String, index=True)  # Nombre del usuario
    image_path = Column(String)  # Ruta de la imagen del usuario (campo de texto)
    is_active = Column(Boolean, default=True)  # Estado del usuario (activo o eliminado lógicamente)

# Creamos las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Función para obtener la sesión de la base de datos
# Se usa "yield" para asegurarnos de que la sesión se cierre después de usarla
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo para la creación de un usuario
class UserCreate(BaseModel):
    name: str  # Solo requiere el nombre
    image_path: str  # Ruta de la imagen (cadena de texto)

# Modelo para la actualización de un usuario
class UserUpdate(BaseModel):
    name: str  # Nuevo nombre del usuario
    image_path: str  # Nueva ruta de la imagen (cadena de texto)

# Endpoint para crear un usuario
@app.post("/users/")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = User(name=user_data.name, image_path=user_data.image_path)  # Creamos el objeto usuario
    db.add(user)  # Agregamos el usuario a la sesión de base de datos
    db.commit()  # Guardamos los cambios en la base de datos
    db.refresh(user)  # Actualizamos el objeto con los datos guardados
    return user  # Devolvemos el usuario creado

# Endpoint para actualizar un usuario
@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()  # Buscamos el usuario por ID
    if not user:
        raise HTTPException(status_code=404, detail="User not found")  # Si no existe, devolvemos un error 404
    
    user.name = user_data.name  # Actualizamos el nombre
    user.image_path = user_data.image_path  # Actualizamos la ruta de la imagen
    db.commit()  # Guardamos los cambios en la base de datos
    return user  # Devolvemos el usuario actualizado

# Endpoint para eliminar un usuario (eliminación lógica)
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()  # Buscamos el usuario por ID
    if not user:
        raise HTTPException(status_code=404, detail="User not found")  # Si no existe, devolvemos un error 404
    
    user.is_active = False  # Marcamos al usuario como inactivo
    db.commit()  # Guardamos los cambios en la base de datos
    return {"message": "User deleted"}  # Confirmamos la eliminación lógica


# Endpoint para listar los usuarios activos
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_active == True).all()  # Obtenemos solo los usuarios activos
    return users  # Retornamos la lista de usuarios


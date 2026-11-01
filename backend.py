import os
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Lee la URL de Neon desde las variables de entorno de Render
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Falta la variable DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define la tabla donde se guardarán las ventas
class VentaDB(Base):
    __tablename__ = "ventas"
    id = Column(Integer, primary_key=True, index=True)
    producto = Column(String)
    monto = Column(Float)
    vendedor = Column(String)
    fecha = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)

# Define los datos que recibirá la API
class VentaInput(BaseModel):
    producto: str
    monto: float
    vendedor: str

app = FastAPI(title="API Sistema de Ventas")

# Endpoint para recibir datos (POST)
@app.post("/api/ventas")
def registrar_venta(venta: VentaInput):
    db = SessionLocal()
    nueva_venta = VentaDB(producto=venta.producto, monto=venta.monto, vendedor=venta.vendedor)
    db.add(nueva_venta)
    db.commit()
    db.refresh(nueva_venta)
    db.close()
    return {"mensaje": "Venta registrada con éxito", "id": nueva_venta.id}

# Endpoint para enviar datos (GET)
@app.get("/api/ventas")
def obtener_ventas():
    db = SessionLocal()
    ventas = db.query(VentaDB).all()
    db.close()
    return ventas

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from database import database, metadata, DATABASE_URL
from routers.productos import router as productos_router
from routers.productos_qr import router as productos_qr_router
from routers.ventas import router as ventas_router
from routers.estadisticas import router as estadisticas_router

app = FastAPI()

# ⚠️ Configuración de CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://almacen-qr.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Esto crea las tablas en la DB si no existen
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

# Tus routers
app.include_router(productos_router, prefix="/productos", tags=["productos"])
app.include_router(productos_qr_router, prefix="/productos_qr", tags=["productos_qr"])
app.include_router(ventas_router, prefix="/ventas", tags=["ventas"])
app.include_router(estadisticas_router, prefix="/estadisticas", tags=["estadisticas"])

@app.on_event("startup")
async def startup():
    print("⏫ Conectando a la DB...")
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

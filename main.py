from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from database import database, metadata, DATABASE_URL
from routers.productos import router as productos_router
from routers.productos_qr import router as productos_qr_router
from routers.ventas import router as ventas_router
from routers.estadisticas import router as estadisticas_router
from routers.consulta_ia import router as consulta_ia_router
from routers.ping import router as ping
from routers.marca_agua import router as marca_agua_router


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
app.include_router(ping, prefix="/ping", tags=["ping"])
app.include_router(productos_router, prefix="/productos", tags=["productos"])
app.include_router(productos_qr_router, prefix="/productos_qr", tags=["productos_qr"])
app.include_router(ventas_router, prefix="/ventas", tags=["ventas"])
app.include_router(estadisticas_router, prefix="/estadisticas", tags=["estadisticas"])
app.include_router(consulta_ia_router, prefix="/consulta_ia", tags=["consulta_ia"])
app.include_router(marca_agua_router, prefix="/marca_agua", tags=["marca_agua"])

@app.on_event("startup")
async def startup():
    print("⏫ Conectando a la DB...")
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

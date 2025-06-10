from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from database import database, productos

router = APIRouter()

class Producto(BaseModel):
    id: int
    codigo: str
    nombre: str
    stock: int
    ubicacion: str
    creado_en: str
    precio: float
    costo: float

def convertir_producto(fila) -> dict:
    return {
        "id": fila["id"],
        "codigo": fila["codigo"] or "",
        "nombre": fila["nombre"] or "",
        "stock": fila["stock"] or 0,
        "ubicacion": fila["ubicacion"] or "",
        "creado_en": fila["creado_en"].isoformat() if fila["creado_en"] else "",
        "precio": float(fila["precio"]) if fila["precio"] is not None else 0.0,
        "costo": float(fila["costo"]) if fila["costo"] is not None else 0.0,
    }

@router.get("/", response_model=List[Producto])
async def listar_productos():
    print("👉 Ejecutando SELECT de productos")
    query = productos.select()
    filas = await database.fetch_all(query)
    return [convertir_producto(fila) for fila in filas]

@router.get("/{producto_id}", response_model=Producto)
async def obtener_producto(producto_id: int):
    query = productos.select().where(productos.c.id == producto_id)
    fila = await database.fetch_one(query)
    if not fila:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return convertir_producto(fila)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_producto(producto: Producto):
    print("Producto recibido:", producto.model_dump())
    query = productos.insert().values(
        codigo=producto.codigo,
        nombre=producto.nombre,
        stock=producto.stock,
        ubicacion=producto.ubicacion,
        precio=producto.precio,
        costo=producto.costo,
    )
    nuevo_id = await database.execute(query)
    return { "id": nuevo_id, **producto.model_dump() }
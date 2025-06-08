from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from database import database, ventas, ventas_detalle

router = APIRouter()

class Venta(BaseModel):
    id: int
    fecha: str

class DetalleVenta(BaseModel):
    id: int
    venta_id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    precio_total: float

def convertir_venta(fila) -> dict:
    return {
        "id": fila["id"],
        "fecha": fila["fecha"] or ""
    }

def convertir_detalle_venta(fila) -> dict:
    return {
        "id": fila["id"],
        "venta_id": fila["venta_id"],
        "producto_id": fila["producto_id"],
        "cantidad": fila["cantidad"],
        "precio_unitario": fila["precio_unitario"],
        "precio_total": fila["precio_total"]
    }

@router.get("/", response_model=List[Venta])
async def listar_ventas():
    filas = await database.fetch_all(ventas.select())
    return [convertir_venta(fila) for fila in filas]

@router.get("/{venta_id}/detalle", response_model=List[DetalleVenta])
async def obtener_detalle_venta(venta_id: int):
    filas = await database.fetch_all(ventas_detalle.select().where(ventas_detalle.c.venta_id == venta_id))
    if not filas:
        raise HTTPException(status_code=404, detail="No hay detalle para esa venta")
    return [convertir_detalle_venta(fila) for fila in filas]

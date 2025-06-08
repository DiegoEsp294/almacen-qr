from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from database import database, productos_qr, productos

router = APIRouter()

class ProductoQR(BaseModel):
    id: int
    producto_id: int
    codigo_qr: str

def convertir_producto_qr(fila) -> dict:
    return {
        "id": fila["id"],
        "producto_id": fila["producto_id"],
        "codigo_qr": fila["codigo_qr"] or ""
    }

@router.get("/", response_model=List[ProductoQR])
async def listar_productos_qr():
    query = productos_qr.select()
    filas = await database.fetch_all(query)
    return [convertir_producto_qr(fila) for fila in filas]

@router.get("/{codigo_qr}", response_model=ProductoQR)
async def obtener_producto_por_qr(codigo_qr: str):
    query = productos_qr.select().where(productos_qr.c.codigo_qr == codigo_qr)
    fila = await database.fetch_one(query)
    if not fila:
        raise HTTPException(status_code=404, detail="QR no encontrado")
    return convertir_producto_qr(fila)

from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel
from database import database, productos_qr, productos

router = APIRouter()

class ProductoQR(BaseModel):
    id: int
    producto_id: int
    codigo_qr: str

class ProductoQRCreate(BaseModel):
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
    query = productos_qr.select().where(productos_qr.c.codigo == codigo_qr)
    fila = await database.fetch_one(query)
    if not fila:
        raise HTTPException(status_code=404, detail="QR no encontrado")
    return convertir_producto_qr(fila)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_producto_qr(producto_qr: ProductoQRCreate):
    query = productos_qr.insert().values(
        producto_id=producto_qr.producto_id,
        codigo_qr=producto_qr.codigo_qr
    )
    last_record_id = await database.execute(query)
    return { "id": last_record_id, **producto_qr.model_dump() }

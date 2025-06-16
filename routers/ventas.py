from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from database import database, ventas, ventas_detalle, productos
from datetime import datetime

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

class DetalleVentaIn(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float

class VentaIn(BaseModel):
    detalles: List[DetalleVentaIn]

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


@router.post("/", status_code=201)
async def crear_venta(venta: VentaIn):
    fecha_actual = datetime.now().isoformat()

    # Insertar venta y obtener id
    query_venta = ventas.insert().values(fecha=fecha_actual)
    venta_id = await database.execute(query_venta)

    # Insertar detalles y actualizar stock
    for detalle in venta.detalles:
        # Insertar detalle
        query_detalle = ventas_detalle.insert().values(
            venta_id=venta_id,
            producto_id=detalle.producto_id,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario,
            precio_total=detalle.cantidad * detalle.precio_unitario
        )
        await database.execute(query_detalle)

        # Actualizar stock (restar cantidad vendida)
        # Primero consulto stock actual
        query_stock = productos.select().where(productos.c.id == detalle.producto_id)
        producto = await database.fetch_one(query_stock)

        if producto is None:
            raise HTTPException(status_code=404, detail=f"Producto {detalle.producto_id} no encontrado")

        nuevo_stock = producto.stock - detalle.cantidad
        if nuevo_stock < 0:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para producto {detalle.producto_id}")

        query_update_stock = productos.update().where(productos.c.id == detalle.producto_id).values(stock=nuevo_stock)
        await database.execute(query_update_stock)

    return {"venta_id": venta_id, "mensaje": "Venta registrada correctamente"}
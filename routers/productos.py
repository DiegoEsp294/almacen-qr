from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from database import database, productos

router = APIRouter()

class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    stock: int
    ubicacion: str
    precio: float
    costo: float

class Producto(ProductoBase):
    id: int
    creado_en: str

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

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Producto)
async def crear_producto(producto: ProductoBase):
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

    query_select = productos.select().where(productos.c.id == nuevo_id)
    fila = await database.fetch_one(query_select)

    return convertir_producto(fila)

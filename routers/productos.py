from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from database import database, productos
from fastapi import UploadFile, Form
import os
import shutil

router = APIRouter()

class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    stock: int
    ubicacion: str
    precio: float
    costo: float
    imagen: str | None = None

class Producto(ProductoBase):
    id: int
    creado_en: str

class ProductoUpdate(BaseModel):
    stock: int

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
        "imagen": fila["imagen"] if "imagen" in fila.keys() else "",
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

from fastapi import UploadFile, Form

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Producto)
async def crear_producto(
    codigo: str = Form(...),
    nombre: str = Form(...),
    stock: int = Form(...),
    ubicacion: str = Form(...),
    precio: float = Form(...),
    costo: float = Form(...),
    file: UploadFile = Form(None)  # ← Opcional
):
    print("Producto recibido:", codigo, nombre, stock, ubicacion, precio, costo)

    # Guardar la imagen si viene
    imagen_path = None
    if file:
        folder = "static/images"
        os.makedirs(folder, exist_ok=True)
        file_location = f"{folder}/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        imagen_path = f"/static/images/{file.filename}"

    # Guardar el producto en la base de datos
    query = productos.insert().values(
        codigo=codigo,
        nombre=nombre,
        stock=stock,
        ubicacion=ubicacion,
        precio=precio,
        costo=costo,
        imagen=imagen_path  # Guardás la ruta o None
    )
    nuevo_id = await database.execute(query)

    query_select = productos.select().where(productos.c.id == nuevo_id)
    fila = await database.fetch_one(query_select)

    return convertir_producto(fila)


@router.put("/{producto_id}", status_code=status.HTTP_200_OK)
async def actualizar_producto_qr(producto_id: int, producto_qr: ProductoUpdate):
    query = productos.update().where(
        productos.c.id == producto_id
    ).values(
        stock=producto_qr.stock
    )
    result = await database.execute(query)
    if result == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return { "id": producto_id, **producto_qr.model_dump() }
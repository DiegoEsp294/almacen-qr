from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from database import database, productos
from fastapi import UploadFile, Form
import os
import shutil
import re

router = APIRouter()

class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    stock: int
    ubicacion: str
    precio: float
    costo: float
    imagen: Optional[str] = None


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


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Producto)
async def crear_producto(
    codigo: str = Form(...),
    nombre: str = Form(...),
    stock: int = Form(...),
    ubicacion: str = Form(...),
    precio: float = Form(...),
    costo: float = Form(...),
    file: UploadFile = Form(None)
):
    print("Producto recibido:", codigo, nombre, stock, ubicacion, precio, costo)

    imagen_path = None
    if file:
        # 📁 Ruta donde se guardan las imágenes
        UPLOAD_FOLDER = "static/images"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ✔️ Crea el folder si no existe

        # Limpia el nombre del archivo (quita caracteres raros y espacios)
        filename_clean = re.sub(r'[^a-zA-Z0-9_.-]', '-', file.filename)

        file_location = os.path.join(UPLOAD_FOLDER, filename_clean)

        # Guarda físicamente la imagen
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Guarda la ruta relativa para después usarla en la web
        imagen_path = f"/static/images/{filename_clean}"

    # Guarda el producto en la base de datos
    query = productos.insert().values(
        codigo=codigo,
        nombre=nombre,
        stock=stock,
        ubicacion=ubicacion,
        precio=precio,
        costo=costo,
        imagen=imagen_path
    )
    nuevo_id = await database.execute(query)

    # Trae el producto recién creado
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
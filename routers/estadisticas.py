from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from database import database, ventas, ventas_detalle, productos
from datetime import datetime, timedelta
from sqlalchemy import func, select, desc
from datetime import date

router = APIRouter()

class ProductoMasVendido(BaseModel):
    id: int
    nombre: str
    cantidad: int

class ProductoHistoricoVentas(BaseModel):
    id: int
    nombre: str
    fecha_venta: date

class Estadisticas(BaseModel):
    total_ventas_hoy: float
    total_ventas_ultima_semana: float
    total_ventas_ultimo_mes: float
    promedio_venta_diaria_ultima_semana: float
    producto_mas_vendido: Optional[ProductoMasVendido]
    historico_ventas: List[ProductoHistoricoVentas]

@router.get("/", response_model=Estadisticas)
async def obtener_estadisticas():
    hoy = datetime.now().date()
    semana_atras = hoy - timedelta(days=7)
    mes_atras = hoy - timedelta(days=30)

    print(hoy)
    print(semana_atras)
    print(mes_atras)

    # Total vendido hoy
    query_total_hoy = select(func.sum(ventas_detalle.c.precio_total)).select_from(
        ventas.join(ventas_detalle, ventas.c.id == ventas_detalle.c.venta_id)
    ).where(func.date(ventas.c.fecha) == hoy)
    total_hoy = await database.fetch_val(query_total_hoy) or 0.0

    # Total vendido última semana
    query_total_semana = select(func.sum(ventas_detalle.c.precio_total)).select_from(
        ventas.join(ventas_detalle, ventas.c.id == ventas_detalle.c.venta_id)
    ).where(ventas.c.fecha >= semana_atras)
    total_semana = await database.fetch_val(query_total_semana) or 0.0

    # Total vendido último mes
    query_total_mes = select(func.sum(ventas_detalle.c.precio_total)).select_from(
        ventas.join(ventas_detalle, ventas.c.id == ventas_detalle.c.venta_id)
    ).where(ventas.c.fecha >= mes_atras)
    total_mes = await database.fetch_val(query_total_mes) or 0.0

    # Producto más vendido
    query_mas_vendido = select(
        productos.c.id,
        productos.c.nombre,
        func.sum(ventas_detalle.c.cantidad).label("total")
    ).select_from(
        productos.join(ventas_detalle, productos.c.id == ventas_detalle.c.producto_id)
    ).group_by(productos.c.id).order_by(desc("total")).limit(1)
    producto = await database.fetch_one(query_mas_vendido)

    if producto:
        producto_mas_vendido = {
            "id": producto["id"],
            "nombre": producto["nombre"],
            "cantidad": producto["total"]
        }
    else:
        producto_mas_vendido = None

    # Productos historico ventas
    query_historico_ventas = """
        SELECT 
            p.id AS id,
            p.nombre AS nombre,
            v.fecha AS fecha_venta
        FROM ventas v
        JOIN ventas_detalle vd ON v.id = vd.venta_id
        JOIN productos p ON p.id = vd.producto_id
        WHERE v.fecha >= :fecha
        ORDER BY v.fecha DESC
    """
    resultados = await database.fetch_all(query_historico_ventas, {"fecha": mes_atras})

    productos_historico_ventas = []
    for fila in resultados:
        productos_historico_ventas.append({
            "id": fila["id"],
            "nombre": fila["nombre"],
            "fecha_venta": fila["fecha_venta"]
        })

    return {
        "total_ventas_hoy": total_hoy,
        "total_ventas_ultima_semana": total_semana,
        "total_ventas_ultimo_mes": total_mes,
        "promedio_venta_diaria_ultima_semana": round(total_semana / 7, 2),
        "producto_mas_vendido": producto_mas_vendido,
        "historico_ventas": productos_historico_ventas
    }

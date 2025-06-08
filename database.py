from databases import Database
from sqlalchemy import Table, Column, Integer, String, Numeric, TIMESTAMP, MetaData, ForeignKey

DATABASE_URL = "mysql+pymysql://root@localhost/qr_db"

database = Database(DATABASE_URL)
metadata = MetaData()

productos = Table(
    "productos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("codigo", String(50)),
    Column("nombre", String(100)),
    Column("stock", Integer),
    Column("ubicacion", String(100)),
    Column("creado_en", TIMESTAMP),
    Column("precio", Numeric(10, 2)),
    Column("costo", Numeric(10, 2)),
)

productos_qr = Table(
    "productos_qr",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("producto_id", Integer, ForeignKey("productos.id")),
    Column("codigo_qr", String(100)),
    Column("creado_en", TIMESTAMP),
)

ventas = Table(
    "ventas",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("fecha", TIMESTAMP),
)

ventas_detalle = Table(
    "ventas_detalle",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("venta_id", Integer, ForeignKey("ventas.id")),
    Column("producto_id", Integer, ForeignKey("productos.id")),
    Column("cantidad", Integer),
    Column("precio_unitario", Numeric(10, 2)),
    Column("precio_total", Numeric(10, 2)),
)

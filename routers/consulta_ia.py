from fastapi import APIRouter, Body
from pydantic import BaseModel
import requests
import os

router = APIRouter()

# API Key de Groq (guardala como variable de entorno en producción)
import os
from dotenv import load_dotenv

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class ConsultaIARequest(BaseModel):
    pregunta: str

class ConsultaIAResponse(BaseModel):
    consulta_sql: str
    resultados: list
    error: str = None

@router.post("/", response_model=ConsultaIAResponse)
async def consultar_por_ia(data: ConsultaIARequest):
    try:
        prompt = f"""
    Base de datos MySQL con estas tablas principales:

    - productos(id INT PK, codigo VARCHAR, nombre VARCHAR, stock INT, ubicacion VARCHAR, precio DECIMAL, costo DECIMAL)
    - productos_historico(id INT PK, producto_id INT FK a productos.id, nombre VARCHAR, precio DECIMAL, costo DECIMAL, accion ENUM, fecha DATETIME)
    - productos_qr(id INT PK, producto_id INT FK a productos.id, codigo_qr VARCHAR)
    - ubicaciones(id INT PK, nombre VARCHAR)
    - ventas(id INT PK, fecha DATETIME)
    - ventas_detalle(id INT PK, venta_id INT FK a ventas.id, producto_id INT FK a productos.id, cantidad INT, precio_unitario DECIMAL, precio_total DECIMAL)
    - usuarios(id_usuarios INT PK, nombre VARCHAR, apellido VARCHAR, email VARCHAR)
    - roles(id_roles INT PK, nombre VARCHAR)

    Relaciones importantes:
    - ventas_detalle.venta_id referencia ventas.id
    - ventas_detalle.producto_id referencia productos.id
    - productos_qr.producto_id referencia productos.id

    Tu tarea es:

    1. Convertir el siguiente pedido en una consulta SQL válida para MySQL. Solo devolvé la consulta, sin explicaciones.

    Pedido del usuario: {data.pregunta}
    """

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0,
            },
        )

        json_data = response.json()

        if response.status_code != 200:
            return {
                "consulta_sql": "",
                "resultados": [],
                "error": f"Groq error: {json_data.get('error', {}).get('message', 'Desconocido')}"
            }

        consulta_sql = json_data["choices"][0]["message"]["content"].strip()


        # Quitar backticks si vienen
        if consulta_sql.startswith("```") and consulta_sql.endswith("```"):
            consulta_sql = "\n".join(consulta_sql.splitlines()[1:-1]).strip()

        # 👇 Ejecutamos la consulta en tu base de datos
        from database import database
        resultados = await database.fetch_all(consulta_sql)

        return {
            "consulta_sql": consulta_sql,
            "resultados": [dict(r) for r in resultados],
        }

    except Exception as e:
        return {
            "consulta_sql": "",
            "resultados": [],
            "error": str(e),
        }

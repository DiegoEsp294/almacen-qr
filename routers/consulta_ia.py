from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
import openai
from dotenv import load_dotenv

# Cargar .env\load_dotenv()

router = APIRouter()
# Usar la clave de OpenAI para ChatGPT
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

class ConsultaIARequest(BaseModel):
    pregunta: str

class ConsultaIAResponse(BaseModel):
    consulta_sql: str
    resultados: list
    respuesta_usuario: str
    error: str = None


def fix_encoding(text: str) -> str:
    """
    Corrige posibles mojibakes re-codificando de latin-1 a utf-8.
    """
    try:
        return text.encode('latin-1').decode('utf-8')
    except Exception:
        return text

@router.post("/", response_model=ConsultaIAResponse)
async def consultar_por_ia(data: ConsultaIARequest):
    try:
        # Paso 1: generar SQL con ChatGPT
        prompt_sql = f"""
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

Además cuando te consulten por fechas, comparalo por la fecha pero sin tener en cuenta la hora, es decir, solo la fecha.

Pedido del usuario: {data.pregunta}
"""
        response_sql = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt_sql}],
            temperature=0
        )
        # Extraer consulta SQL
        consulta_raw = response_sql.choices[0].message.content.strip()
        if consulta_raw.startswith("```") and consulta_raw.endswith("```"):
            consulta_raw = "\n".join(consulta_raw.splitlines()[1:-1]).strip()
        consulta_sql = fix_encoding(consulta_raw)

        # Paso 2: ejecutar SQL en la DB
        from database import database
        resultados = await database.fetch_all(consulta_sql)
        resultados_list = [dict(r) for r in resultados]

        # Paso 3: generar respuesta natural con ChatGPT
        prompt_respuesta = f"""
Pedido del usuario: {data.pregunta}
Resultado de la consulta (formato lista de diccionarios): {resultados_list}

Respondé como si fueras un asistente de datos. Sé claro, profesional y directo. No muestres código ni SQL.
"""
        response_txt = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt_respuesta}],
            temperature=0.3
        )
        respuesta_raw = response_txt.choices[0].message.content.strip()
        respuesta_usuario = fix_encoding(respuesta_raw)

        return ConsultaIAResponse(
            consulta_sql=consulta_sql,
            resultados=resultados_list,
            respuesta_usuario=respuesta_usuario,
        )

    except Exception as e:
        return ConsultaIAResponse(
            consulta_sql="",
            resultados=[],
            respuesta_usuario="",
            error=str(e),
        )

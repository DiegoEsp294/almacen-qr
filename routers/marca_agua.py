from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from PIL import Image, ImageEnhance
import base64
import io
import os

router = APIRouter()

class ImagenRequest(BaseModel):
    imagen_base64: str

def agregar_marca_agua(imagen_base64: str, watermark_path: str) -> str:
    try:
        # Decodificar la imagen base64
        imagen_bytes = base64.b64decode(imagen_base64)
        imagen = Image.open(io.BytesIO(imagen_bytes)).convert("RGBA")

        # Cargar marca de agua y ajustar su opacidad
        marca = Image.open(watermark_path).convert("RGBA")
        alpha = marca.getchannel("A")
        alpha = ImageEnhance.Brightness(alpha).enhance(0.2)  # 20% opacidad
        marca.putalpha(alpha)

        # Redimensionar si es necesario
        marca = marca.resize((int(imagen.width * 0.3), int(imagen.height * 0.3)))

        # Posición inferior derecha
        pos = (imagen.width - marca.width - 10, imagen.height - marca.height - 10)

        # Pegar la marca sobre la imagen
        imagen.paste(marca, pos, marca)

        # Convertir a base64
        buffer = io.BytesIO()
        imagen.convert("RGB").save(buffer, format="PNG")
        resultado_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return resultado_base64

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def endpoint_marca_agua(data: ImagenRequest):
    # Ruta base del proyecto
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    watermark_path = os.path.join(BASE_DIR, "..", "img", "watermark.png")
    watermark_path = os.path.abspath(watermark_path)

    if not os.path.exists(watermark_path):
        raise HTTPException(status_code=404, detail="Marca de agua no encontrada")

    imagen_con_marca = agregar_marca_agua(data.imagen_base64, watermark_path)
    return {"imagen_con_marca_base64": imagen_con_marca}

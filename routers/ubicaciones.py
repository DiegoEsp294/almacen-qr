from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Ubicacion(BaseModel):
    id: Optional[int] = None
    nombre: str

ubicaciones = []

@router.get("/", response_model=List[Ubicacion])
def listar_ubicaciones():
    return ubicaciones

@router.post("/", response_model=Ubicacion)
def crear_ubicacion(ubicacion: Ubicacion):
    ubicacion.id = len(ubicaciones) + 1
    ubicaciones.append(ubicacion)
    return ubicacion

@router.get("/{ubicacion_id}", response_model=Ubicacion)
def obtener_ubicacion(ubicacion_id: int):
    for u in ubicaciones:
        if u.id == ubicacion_id:
            return u
    raise HTTPException(status_code=404, detail="Ubicación no encontrada")

@router.put("/{ubicacion_id}", response_model=Ubicacion)
def actualizar_ubicacion(ubicacion_id: int, ubicacion: Ubicacion):
    for i, u in enumerate(ubicaciones):
        if u.id == ubicacion_id:
            ubicaciones[i] = ubicacion
            ubicaciones[i].id = ubicacion_id
            return ubicaciones[i]
    raise HTTPException(status_code=404, detail="Ubicación no encontrada")

@router.delete("/{ubicacion_id}")
def eliminar_ubicacion(ubicacion_id: int):
    for i, u in enumerate(ubicaciones):
        if u.id == ubicacion_id:
            ubicaciones.pop(i)
            return {"msg": "Ubicación eliminada"}
    raise HTTPException(status_code=404, detail="Ubicación no encontrada")

# db_schema.py
from pydantic import BaseModel
from typing import Optional

class RegistroFalla(BaseModel):
    """Modelo de Pydantic para validar los datos que llegan de la cámara Android."""
    
    # Datos de GPS (el cliente los envía)
    latitud: float
    longitud: float
    
    # Datos de Visión Computacional (Resultado de YOLO)
    nombre_falla_detectada: str
    nivel_confianza: float
    
    # Datos Opcionales (para referencia)
    url_imagen: Optional[str] = None
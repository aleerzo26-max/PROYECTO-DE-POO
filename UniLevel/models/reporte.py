from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Reporte:
    id: str
    usuario_id: Any
    tipo: str
    formato: str
    nombre_archivo: str
    ruta_archivo: str
    fecha_generacion: str
    descripcion: str

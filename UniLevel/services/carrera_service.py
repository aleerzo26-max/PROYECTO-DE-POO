from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from repositories.carrera_repository import CarreraRepository


class CarreraService:
    def __init__(self, carrera_repository: CarreraRepository) -> None:
        self._carrera_repository = carrera_repository

    def listar_carreras(self) -> List[Dict[str, Any]]:
        return self._carrera_repository.obtener_todos()

    def crear_carrera(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        datos_obj = {
            "id": str(uuid.uuid4()),
            "nombre": datos.get("nombre", "").strip(),
            "codigo": datos.get("codigo", "").strip(),
            "descripcion": datos.get("descripcion", "").strip(),
        }
        return self._carrera_repository.guardar(datos_obj)

    def obtener_carrera(self, carrera_id: Any) -> Optional[Dict[str, Any]]:
        return self._carrera_repository.obtener_por_id(carrera_id)

    def editar_carrera(self, carrera_id: Any, datos: Dict[str, Any]) -> bool:
        return self._carrera_repository.actualizar(carrera_id, datos)

    def eliminar_carrera(self, carrera_id: Any) -> bool:
        return self._carrera_repository.eliminar(carrera_id)

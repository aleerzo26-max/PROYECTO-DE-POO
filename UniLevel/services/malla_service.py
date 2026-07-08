from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from repositories.malla_repository import MallaRepository


class MallaService:
    def __init__(self, malla_repository: MallaRepository) -> None:
        self._malla_repository = malla_repository

    def listar_mallas(self) -> List[Dict[str, Any]]:
        return self._malla_repository.obtener_todos()

    def crear_malla(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        datos_obj = {
            "id": str(uuid.uuid4()),
            "nombre": datos.get("nombre", "").strip(),
            "carrera_id": datos.get("carrera_id"),
            "descripcion": datos.get("descripcion", "").strip(),
            "asignaturas": datos.get("asignaturas", []),
        }
        return self._malla_repository.guardar(datos_obj)

    def obtener_malla(self, malla_id: Any) -> Optional[Dict[str, Any]]:
        return self._malla_repository.obtener_por_id(malla_id)

    def editar_malla(self, malla_id: Any, datos: Dict[str, Any]) -> bool:
        return self._malla_repository.actualizar(malla_id, datos)

    def eliminar_malla(self, malla_id: Any) -> bool:
        return self._malla_repository.eliminar(malla_id)

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from repositories.asignatura_repository import AsignaturaRepository


class AsignaturaService:
    def __init__(self, asignatura_repository: AsignaturaRepository) -> None:
        self._asignatura_repository = asignatura_repository

    def listar_asignaturas(self) -> List[Dict[str, Any]]:
        return self._asignatura_repository.obtener_todos()

    def crear_asignatura(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        datos_obj = {
            "id": str(uuid.uuid4()),
            "nombre": datos.get("nombre", "").strip(),
            "codigo": datos.get("codigo", "").strip(),
            "creditos": datos.get("creditos", 0),
            "descripcion": datos.get("descripcion", "").strip(),
        }
        return self._asignatura_repository.guardar(datos_obj)

    def obtener_asignatura(self, asignatura_id: Any) -> Optional[Dict[str, Any]]:
        return self._asignatura_repository.obtener_por_id(asignatura_id)

    def editar_asignatura(self, asignatura_id: Any, datos: Dict[str, Any]) -> bool:
        return self._asignatura_repository.actualizar(asignatura_id, datos)

    def eliminar_asignatura(self, asignatura_id: Any) -> bool:
        return self._asignatura_repository.eliminar(asignatura_id)

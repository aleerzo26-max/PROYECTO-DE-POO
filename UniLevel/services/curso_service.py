from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from repositories.curso_repository import CursoRepository


class CursoService:
    def __init__(self, curso_repository: CursoRepository) -> None:
        self._curso_repository = curso_repository

    def listar_cursos(self) -> List[Dict[str, Any]]:
        return self._curso_repository.obtener_todos()

    def crear_curso(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        datos_obj = {
            "id": str(uuid.uuid4()),
            "nombre": datos.get("nombre", "").strip(),
            "asignatura_id": datos.get("asignatura_id"),
            "malla_id": datos.get("malla_id"),
            "descripcion": datos.get("descripcion", "").strip(),
        }
        return self._curso_repository.guardar(datos_obj)

    def obtener_curso(self, curso_id: Any) -> Optional[Dict[str, Any]]:
        return self._curso_repository.obtener_por_id(curso_id)

    def editar_curso(self, curso_id: Any, datos: Dict[str, Any]) -> bool:
        return self._curso_repository.actualizar(curso_id, datos)

    def eliminar_curso(self, curso_id: Any) -> bool:
        return self._curso_repository.eliminar(curso_id)

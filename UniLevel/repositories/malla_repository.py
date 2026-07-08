from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class MallaRepository(BaseRepository):
    """Repositorio para la persistencia de mallas curriculares."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        for m in self.obtener_todos():
            if isinstance(m, dict) and m.get("id") == id:
                return m
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class ParaleloRepository(BaseRepository):
    """Repositorio para la persistencia de paralelos en archivos JSON."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los paralelos almacenados."""
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene un paralelo por su identificador."""
        for paralelo in self.obtener_todos():
            if isinstance(paralelo, dict) and paralelo.get("id") == id:
                return paralelo
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda un nuevo paralelo en el repositorio."""
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        """Actualiza un paralelo existente."""
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        """Elimina un paralelo por su identificador."""
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

    def existe_paralelo(self, paralelo_id: Any) -> bool:
        """Verifica si un paralelo existe en el repositorio."""
        return self.obtener_por_id(paralelo_id) is not None

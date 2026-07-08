from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class EntregaRepository(BaseRepository):
    """Repositorio para la persistencia de entregas de tareas en archivos JSON."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todas las entregas almacenadas."""
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene una entrega por su identificador."""
        for entrega in self.obtener_todos():
            if isinstance(entrega, dict) and entrega.get("id") == id:
                return entrega
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda una nueva entrega en el repositorio."""
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        """Actualiza una entrega existente."""
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        """Elimina una entrega por su identificador."""
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

    def buscar_por_tarea(self, tarea_id: Any) -> List[Dict[str, Any]]:
        """Busca entregas asociadas a una tarea."""
        return [
            entrega
            for entrega in self.obtener_todos()
            if isinstance(entrega, dict) and entrega.get("tarea_id") == tarea_id
        ]

    def buscar_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Busca entregas realizadas por un estudiante."""
        return [
            entrega
            for entrega in self.obtener_todos()
            if isinstance(entrega, dict) and entrega.get("estudiante_id") == estudiante_id
        ]

    def buscar_por_tarea_y_estudiante(self, tarea_id: Any, estudiante_id: Any) -> Optional[Dict[str, Any]]:
        """Busca una entrega específica de un estudiante para una tarea."""
        for entrega in self.obtener_todos():
            if (
                isinstance(entrega, dict)
                and entrega.get("tarea_id") == tarea_id
                and entrega.get("estudiante_id") == estudiante_id
            ):
                return entrega
        return None

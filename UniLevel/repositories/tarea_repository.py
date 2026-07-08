from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class TareaRepository(BaseRepository):
    """Repositorio para la persistencia de tareas en archivos JSON."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todas las tareas almacenadas."""
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene una tarea por su identificador."""
        for tarea in self.obtener_todos():
            if isinstance(tarea, dict) and tarea.get("id") == id:
                return tarea
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda una nueva tarea en el repositorio."""
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        """Actualiza una tarea existente."""
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        """Elimina una tarea por su identificador."""
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

    def buscar_por_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        """Busca tareas asignadas a un docente."""
        return [
            tarea
            for tarea in self.obtener_todos()
            if isinstance(tarea, dict) and tarea.get("docente_id") == docente_id
        ]

    def buscar_por_paralelo(self, paralelo_id: Any) -> List[Dict[str, Any]]:
        """Busca tareas vinculadas a un paralelo."""
        return [
            tarea
            for tarea in self.obtener_todos()
            if isinstance(tarea, dict) and tarea.get("paralelo_id") == paralelo_id
        ]

    def buscar_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Busca tareas asociadas a un estudiante."""
        return [
            tarea
            for tarea in self.obtener_todos()
            if isinstance(tarea, dict) and tarea.get("estudiante_id") == estudiante_id
        ]

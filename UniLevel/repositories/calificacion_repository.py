from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class CalificacionRepository(BaseRepository):
    """Repositorio para la persistencia de calificaciones en archivos JSON."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todas las calificaciones almacenadas."""
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene una calificación por su identificador."""
        for calificacion in self.obtener_todos():
            if isinstance(calificacion, dict) and calificacion.get("id") == id:
                return calificacion
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda una nueva calificación en el repositorio."""
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        """Actualiza una calificación existente."""
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        """Elimina una calificación por su identificador."""
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

    def buscar_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Busca calificaciones asociadas a un estudiante."""
        return [
            calificacion
            for calificacion in self.obtener_todos()
            if isinstance(calificacion, dict) and calificacion.get("estudiante_id") == estudiante_id
        ]

    def buscar_por_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        """Busca calificaciones registradas por un docente."""
        return [
            calificacion
            for calificacion in self.obtener_todos()
            if isinstance(calificacion, dict) and calificacion.get("docente_id") == docente_id
        ]

    def buscar_por_paralelo(self, paralelo_id: Any) -> List[Dict[str, Any]]:
        """Busca calificaciones asociadas a un paralelo."""
        return [
            calificacion
            for calificacion in self.obtener_todos()
            if isinstance(calificacion, dict) and calificacion.get("paralelo_id") == paralelo_id
        ]

    def buscar_por_evaluacion(self, evaluacion_id: Any) -> List[Dict[str, Any]]:
        """Busca calificaciones asociadas a una evaluación."""
        return [
            calificacion
            for calificacion in self.obtener_todos()
            if isinstance(calificacion, dict) and calificacion.get("evaluacion_id") == evaluacion_id
        ]

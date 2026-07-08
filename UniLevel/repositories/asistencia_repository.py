from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class AsistenciaRepository(BaseRepository):
    """Repositorio para la persistencia de asistencias en archivos JSON."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todas las asistencias almacenadas."""
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene un registro de asistencia por su identificador."""
        for asistencia in self.obtener_todos():
            if isinstance(asistencia, dict) and asistencia.get("id") == id:
                return asistencia
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda un nuevo registro de asistencia."""
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        """Actualiza un registro de asistencia existente."""
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        """Elimina un registro de asistencia por su identificador."""
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

    def buscar_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Busca asistencias registradas para un estudiante."""
        return [
            asistencia
            for asistencia in self.obtener_todos()
            if isinstance(asistencia, dict) and asistencia.get("estudiante_id") == estudiante_id
        ]

    def buscar_por_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        """Busca asistencias registradas por un docente."""
        return [
            asistencia
            for asistencia in self.obtener_todos()
            if isinstance(asistencia, dict) and asistencia.get("docente_id") == docente_id
        ]

    def buscar_por_paralelo(self, paralelo_id: Any) -> List[Dict[str, Any]]:
        """Busca asistencias registradas en un paralelo específico."""
        return [
            asistencia
            for asistencia in self.obtener_todos()
            if isinstance(asistencia, dict) and asistencia.get("paralelo_id") == paralelo_id
        ]

    def buscar_por_estudiante_y_fecha(self, estudiante_id: Any, fecha: str) -> List[Dict[str, Any]]:
        """Busca registros de asistencia de un estudiante en una fecha específica."""
        return [
            asistencia
            for asistencia in self.obtener_todos()
            if isinstance(asistencia, dict)
            and asistencia.get("estudiante_id") == estudiante_id
            and asistencia.get("fecha") == fecha
        ]

    def buscar_por_fecha(self, fecha: str) -> List[Dict[str, Any]]:
        """Busca asistencias registradas en una fecha específica."""
        return [
            asistencia
            for asistencia in self.obtener_todos()
            if isinstance(asistencia, dict) and asistencia.get("fecha") == fecha
        ]

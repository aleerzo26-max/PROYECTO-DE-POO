from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class HorarioRepository(BaseRepository):
    """Repositorio para la persistencia de horarios académicos."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        for horario in self.obtener_todos():
            if isinstance(horario, dict) and horario.get("id") == id:
                return horario
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

    def obtener_por_matricula(self, matricula_id: Any) -> Optional[Dict[str, Any]]:
        for horario in self.obtener_todos():
            if isinstance(horario, dict) and horario.get("matricula_id") == matricula_id:
                return horario
        return None

    def buscar_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        return [
            horario
            for horario in self.obtener_todos()
            if isinstance(horario, dict) and horario.get("estudiante_id") == estudiante_id
        ]

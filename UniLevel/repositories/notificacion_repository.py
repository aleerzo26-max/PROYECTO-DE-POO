from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class NotificacionRepository(BaseRepository):
    """Repositorio para la persistencia de notificaciones en archivos JSON."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        for notificacion in self.obtener_todos():
            if isinstance(notificacion, dict) and notificacion.get("id") == id:
                return notificacion
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

    def buscar_por_usuario(self, usuario_id: Any) -> List[Dict[str, Any]]:
        return [
            notificacion
            for notificacion in self.obtener_todos()
            if isinstance(notificacion, dict) and notificacion.get("usuario_id") == usuario_id
        ]

    def buscar_por_usuario_y_estado(self, usuario_id: Any, leida: bool) -> List[Dict[str, Any]]:
        return [
            notificacion
            for notificacion in self.obtener_todos()
            if isinstance(notificacion, dict)
            and notificacion.get("usuario_id") == usuario_id
            and bool(notificacion.get("leida", False)) == leida
        ]

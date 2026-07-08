from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from repositories.notificacion_repository import NotificacionRepository


class NotificacionService:
    """Servicio responsable de la creación y gestión de notificaciones internas."""

    def __init__(self, notificacion_repository: Optional[NotificacionRepository] = None) -> None:
        self._notificacion_repository = notificacion_repository

    def crear_notificacion(self, usuario_id: Any, titulo: str, mensaje: str) -> Dict[str, Any]:
        """Crea y persiste una notificación interna para un usuario."""
        notificacion = {
            "id": str(uuid.uuid4()),
            "usuario_id": usuario_id,
            "titulo": titulo,
            "mensaje": mensaje,
            "fecha": datetime.utcnow().isoformat(),
            "leida": False,
        }

        if self._notificacion_repository is not None:
            return self._notificacion_repository.guardar(notificacion)

        return notificacion

    def crear_notificacion_con_meta(self, usuario_id: Any, titulo: str, mensaje: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crea una notificación con metadatos adicionales (por ejemplo credenciales temporales)."""
        notificacion = {
            "id": str(uuid.uuid4()),
            "usuario_id": usuario_id,
            "titulo": titulo,
            "mensaje": mensaje,
            "fecha": datetime.utcnow().isoformat(),
            "leida": False,
            "meta": meta or {},
        }

        if self._notificacion_repository is not None:
            return self._notificacion_repository.guardar(notificacion)

        return notificacion

    def listar_por_usuario(self, usuario_id: Any) -> List[Dict[str, Any]]:
        """Lista las notificaciones ordenadas por fecha del usuario."""
        if self._notificacion_repository is None:
            return []

        notificaciones = self._notificacion_repository.buscar_por_usuario(usuario_id)
        return sorted(notificaciones, key=lambda n: n.get("fecha", ""), reverse=True)

    def listar_recientes_por_usuario(self, usuario_id: Any, limite: int = 5) -> List[Dict[str, Any]]:
        """Lista las notificaciones más recientes de un usuario."""
        return self.listar_por_usuario(usuario_id)[:limite]

    def contar_notificaciones_no_leidas(self, usuario_id: Any) -> int:
        """Cuenta las notificaciones no leídas de un usuario."""
        return sum(
            1 for notificacion in self.listar_por_usuario(usuario_id)
            if not notificacion.get("leida", False)
        )

    def marcar_como_leida(self, notificacion_id: Any, usuario_id: Any) -> Dict[str, Any]:
        """Marca una notificación como leída."""
        if self._notificacion_repository is None:
            raise RuntimeError("Repositorio de notificaciones no configurado.")

        notificacion = self._notificacion_repository.obtener_por_id(notificacion_id)
        if not notificacion or notificacion.get("usuario_id") != usuario_id:
            raise PermissionError("Notificación no encontrada o acceso denegado.")

        if not notificacion.get("leida", False):
            actualizado = {**notificacion, "leida": True}
            if not self._notificacion_repository.actualizar(notificacion_id, actualizado):
                raise RuntimeError("No se pudo actualizar el estado de la notificación.")
            return actualizado

        return notificacion

    def marcar_todas_como_leidas(self, usuario_id: Any) -> int:
        """Marca todas las notificaciones de un usuario como leídas."""
        if self._notificacion_repository is None:
            raise RuntimeError("Repositorio de notificaciones no configurado.")

        contador = 0
        for notificacion in self.listar_por_usuario(usuario_id):
            if not notificacion.get("leida", False):
                actualizado = {**notificacion, "leida": True}
                if self._notificacion_repository.actualizar(notificacion["id"], actualizado):
                    contador += 1

        return contador

    def eliminar_notificacion(self, notificacion_id: Any, usuario_id: Any) -> bool:
        """Elimina una notificación del usuario."""
        if self._notificacion_repository is None:
            raise RuntimeError("Repositorio de notificaciones no configurado.")

        notificacion = self._notificacion_repository.obtener_por_id(notificacion_id)
        if not notificacion or notificacion.get("usuario_id") != usuario_id:
            raise PermissionError("Notificación no encontrada o acceso denegado.")

        return self._notificacion_repository.eliminar(notificacion_id)

    def eliminar_credenciales_temporales_por_usuario(self, usuario_id: Any) -> int:
        """Elimina todas las notificaciones que contengan credenciales temporales asociadas a un usuario."""
        if self._notificacion_repository is None:
            raise RuntimeError("Repositorio de notificaciones no configurado.")

        contador = 0
        todas = self._notificacion_repository.obtener_todos()
        for noti in list(todas):
            meta = noti.get("meta") if isinstance(noti, dict) else None
            if isinstance(meta, dict) and meta.get("tipo") == "credencial_temporal" and meta.get("usuario_id") == usuario_id:
                try:
                    if self._notificacion_repository.eliminar(noti.get("id")):
                        contador += 1
                except Exception:
                    pass

        return contador

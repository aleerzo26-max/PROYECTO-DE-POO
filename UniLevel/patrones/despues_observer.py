"""Ejemplo usando Observer para el mismo caso de uso.

Este archivo muestra el mismo escenario que en antes_observer.py, pero con
una separación clara de responsabilidades:
- Subject emite el evento.
- NotificacionObserver crea la notificación interna.
- EmailObserver prepara el correo.
- AuditoriaObserver registra la auditoría.

La diferencia clave es que el servicio no sabe cómo reaccionar a cada evento;
solo publica y deja que los observadores reaccionen.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from observers.subject import Subject
from observers.notificacion_observer import NotificacionObserver
from observers.email_observer import EmailObserver
from observers.auditoria_observer import AuditoriaObserver
from repositories.notificacion_repository import NotificacionRepository
from services.notificacion_service import NotificacionService


class UsuarioServiceConObserver:
    """Versión refactorizada con Observer para desacoplar acciones secundarias."""

    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parent.parent
        notificaciones_path = base_dir / "data" / "notificaciones.json"
        auditoria_path = base_dir / "data" / "auditoria.json"
        notificacion_repo = NotificacionRepository(str(notificaciones_path))
        notificacion_service = NotificacionService(notificacion_repo)

        self._subject = Subject()
        self._subject.agregar_observer(NotificacionObserver(notificacion_service))
        self._subject.agregar_observer(EmailObserver())
        self._subject.agregar_observer(AuditoriaObserver(str(auditoria_path)))

    def crear_usuario(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        # Comparación con la implementación anterior:
        # ahora el servicio solo prepara el objeto de negocio y publica un evento.
        usuario = {
            "id": "usuario-002",
            "nombre": datos["nombre"],
            "apellido": datos["apellido"],
            "email": datos["email"],
        }
        self._subject.notificar("usuario_creado", {"usuario": usuario})
        return usuario


if __name__ == "__main__":
    servicio = UsuarioServiceConObserver()
    servicio.crear_usuario({"nombre": "Carlos", "apellido": "Paredes", "email": "carlos@uni.com"})

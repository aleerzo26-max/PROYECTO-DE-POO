"""Ejemplo funcional del patrón Observer para UniLevel.

Este script demuestra el flujo del patrón sin depender del sistema principal.
Ejecuta los mismos observadores usados por la fachada de la aplicación.
"""

from __future__ import annotations

from pathlib import Path

from observers.subject import Subject
from observers.notificacion_observer import NotificacionObserver
from observers.email_observer import EmailObserver
from observers.auditoria_observer import AuditoriaObserver
from repositories.notificacion_repository import NotificacionRepository
from services.notificacion_service import NotificacionService


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    notificaciones_path = base_dir / "data" / "notificaciones.json"
    auditoria_path = base_dir / "data" / "auditoria.json"

    notificacion_service = NotificacionService(NotificacionRepository(str(notificaciones_path)))

    subject = Subject()
    subject.agregar_observer(NotificacionObserver(notificacion_service))
    subject.agregar_observer(EmailObserver())
    subject.agregar_observer(AuditoriaObserver(str(auditoria_path)))

    usuario = {
        "id": "usuario-demo",
        "nombre": "Administrador",
        "apellido": "UniLevel",
        "email": "admin@unilevel.edu.ec",
    }

    subject.notificar("usuario_creado", {"usuario": usuario})

    print("Usuario creado correctamente.")
    print("Observer:")
    print("✔ Notificación creada.")
    print("✔ Correo preparado para enviar.")
    print("✔ Auditoría registrada.")


if __name__ == "__main__":
    main()

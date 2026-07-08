from __future__ import annotations

from typing import Any

try:
    from observers.observer import Observer
    from services.notificacion_service import NotificacionService
except ImportError:
    from UniLevel.observers.observer import Observer
    from UniLevel.services.notificacion_service import NotificacionService


class NotificacionObserver(Observer):
    """Observador que crea notificaciones internas para los eventos de negocio."""

    def __init__(self, notificacion_service: NotificacionService) -> None:
        self._notificacion_service = notificacion_service

    def update(self, evento: str, datos: Any) -> None:
        if not isinstance(datos, dict):
            return

        usuario_id = None
        titulo = None
        mensaje = None

        if evento == "usuario_creado":
            usuario = datos.get("usuario")
            usuario_id = usuario.get("id") if isinstance(usuario, dict) else None
            titulo = "Bienvenido a UniLevel"
            mensaje = (
                "Tu cuenta ha sido creada exitosamente. "
                "Revisa tu perfil y cambia tu contraseña temporal."
            )

        elif evento == "estudiante_matriculado":
            matricula = datos.get("matricula")
            usuario_id = matricula.get("estudiante_id") if isinstance(matricula, dict) else None
            titulo = "Matrícula confirmada"
            mensaje = "Tu matrícula ha sido confirmada y tu horario está disponible en el sistema."

        elif evento == "tarea_creada":
            tarea = datos.get("tarea")
            usuario_id = tarea.get("docente_id") if isinstance(tarea, dict) else None
            titulo = "Tarea publicada"
            mensaje = f"La tarea '{tarea.get('titulo', 'Sin título')}' se ha creado correctamente."

        elif evento == "calificacion_publicada":
            calificacion = datos.get("calificacion")
            usuario_id = calificacion.get("estudiante_id") if isinstance(calificacion, dict) else None
            titulo = "Nueva calificación disponible"
            mensaje = (
                f"Se ha registrado la calificación {calificacion.get('nota', 'N/D')} "
                f"para la evaluación '{calificacion.get('evaluacion', 'Sin evaluación')}'."
            )

        elif evento == "docente_asignado":
            paralelo = datos.get("paralelo")
            usuario_id = paralelo.get("docente_id") if isinstance(paralelo, dict) else None
            titulo = "Has sido asignado a un paralelo"
            mensaje = (
                f"Se te ha asignado como docente al paralelo '{paralelo.get('curso_nombre', paralelo.get('nombre', ''))}'."
            )

        if usuario_id and titulo and mensaje and self._notificacion_service is not None:
            self._notificacion_service.crear_notificacion(usuario_id, titulo, mensaje)

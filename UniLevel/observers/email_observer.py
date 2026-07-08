from __future__ import annotations

from typing import Any

try:
    from observers.observer import Observer
    from utils.email_sender import EmailSender
except ImportError:
    from UniLevel.observers.observer import Observer
    from UniLevel.utils.email_sender import EmailSender


class EmailObserver(Observer):
    """Observador que prepara correos electrónicos para los eventos del sistema.

    Por ahora se prepara el contenido del correo y no se envía realmente por SMTP.
    La integración real con un servicio de correo deberá añadirse en
    EmailSender.enviar(...) cuando el proyecto lo requiera.
    """

    def __init__(self) -> None:
        self._email_sender = EmailSender()

    def update(self, evento: str, datos: Any) -> None:
        if not isinstance(datos, dict):
            return

        asunto = None
        cuerpo = None
        destinatario = None

        if evento == "usuario_creado":
            usuario = datos.get("usuario")
            destinatario = usuario.get("email") if isinstance(usuario, dict) else None
            asunto = "Bienvenido a UniLevel"
            cuerpo = "Tu cuenta ha sido creada. Pronto recibirás instrucciones para iniciar sesión."

        elif evento == "estudiante_matriculado":
            matricula = datos.get("matricula")
            destinatario = matricula.get("estudiante_email") if isinstance(matricula, dict) else None
            asunto = "Matrícula confirmada"
            cuerpo = "Tu matrícula ha sido registrada correctamente en UniLevel."

        elif evento == "tarea_creada":
            tarea = datos.get("tarea")
            destinatario = tarea.get("docente_email") if isinstance(tarea, dict) else None
            asunto = "Tarea publicada"
            cuerpo = f"La tarea '{tarea.get('titulo', '')}' se ha publicado correctamente."

        elif evento == "calificacion_publicada":
            calificacion = datos.get("calificacion")
            destinatario = calificacion.get("estudiante_email") if isinstance(calificacion, dict) else None
            asunto = "Nueva calificación disponible"
            cuerpo = (
                f"Se ha registrado tu calificación {calificacion.get('nota', '')} "
                f"para '{calificacion.get('evaluacion', '')}'."
            )

        elif evento == "docente_asignado":
            paralelo = datos.get("paralelo")
            destinatario = paralelo.get("docente_email") if isinstance(paralelo, dict) else None
            asunto = "Asignación de paralelo"
            cuerpo = (
                f"Has sido asignado al paralelo '{paralelo.get('curso_nombre', paralelo.get('nombre', ''))}'."
            )

        if destinatario and asunto and cuerpo:
            self._email_sender.preparar_envio(destinatario, asunto, cuerpo)
            print("Correo preparado para enviar al usuario.")

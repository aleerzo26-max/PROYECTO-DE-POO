from typing import Any, Dict


class EmailSender:
    """Cliente de correo para preparar y enviar notificaciones por email."""

    def preparar_envio(self, destinatario: str, asunto: str, cuerpo: str) -> Dict[str, Any]:
        """Prepara los datos del correo electrónico para envío posterior."""
        correo = {
            "destinatario": destinatario,
            "asunto": asunto,
            "cuerpo": cuerpo,
        }
        return correo

    def enviar(self, correo: Dict[str, Any]) -> bool:
        """Placeholder para enviar un correo electrónico.

        La lógica de envío real se implementará cuando se integre un proveedor de correo.
        """
        return True

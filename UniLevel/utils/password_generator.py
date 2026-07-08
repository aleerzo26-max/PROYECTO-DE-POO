import random
import string


class PasswordGenerator:
    """Generador de contraseñas para el sistema UniLevel."""

    @staticmethod
    def generar_contrasena_temporal(length: int = 12) -> str:
        """Genera una contraseña temporal segura y aleatoria."""
        caracteres = string.ascii_letters + string.digits + string.punctuation
        return "".join(random.choice(caracteres) for _ in range(length))

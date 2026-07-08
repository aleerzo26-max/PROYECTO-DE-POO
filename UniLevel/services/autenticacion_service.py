from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional

from repositories.usuario_repository import UsuarioRepository


class AutenticacionService:
    """Servicio responsable de la lógica de autenticación de usuarios."""

    def __init__(self, usuario_repository: UsuarioRepository) -> None:
        self._usuario_repository = usuario_repository

    def iniciar_sesion(self, correo: str, password: str) -> Dict[str, Any]:
        """Valida las credenciales y retorna la información del usuario autenticado."""
        usuario = self._usuario_repository.buscar_por_correo(correo)
        if usuario is None:
            raise ValueError("Credenciales inválidas.")

        if not self._comparar_password(password, usuario.get("password_hash", "")):
            raise ValueError("Credenciales inválidas.")

        return usuario

    def cerrar_sesion(self) -> None:
        """Finaliza la sesión del usuario.

        Este método es un placeholder. La implementación concreta se hará
        cuando se integre un gestor de sesiones o contexto de autenticación.
        """
        pass

    def cambiar_password(self, usuario_id: Any, nueva_password: str) -> bool:
        """Actualiza la contraseña de un usuario y marca que ya no es el primer inicio."""
        usuario = self._usuario_repository.obtener_por_id(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado.")

        password_hash = self._hash_password(nueva_password)
        datos_actualizados = {
            "password_hash": password_hash,
            "password_temporal": False,
            "primer_inicio": False,
        }

        return self._usuario_repository.actualizar(usuario_id, datos_actualizados)

    def verificar_primer_inicio(self, usuario_id: Any) -> bool:
        """Verifica si el usuario se encuentra en su primer inicio de sesión."""
        usuario = self._usuario_repository.obtener_por_id(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado.")
        return bool(usuario.get("primer_inicio", False))

    @staticmethod
    def _hash_password(password: str) -> str:
        """Genera un hash seguro de la contraseña."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _comparar_password(password: str, password_hash: str) -> bool:
        """Compara una contraseña en texto plano con su hash."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest() == password_hash

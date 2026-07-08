from __future__ import annotations

from typing import Any, Dict, Type, TypeVar

T = TypeVar("T", bound="Credencial")


class Credencial:
    """Modelo de credencial para la autenticación de usuarios."""

    def __init__(
        self,
        username: str,
        password_hash: str,
        usuario_id: str,
    ) -> None:
        self._username = username
        self._password_hash = password_hash
        self._usuario_id = usuario_id

    @property
    def username(self) -> str:
        """Devuelve el nombre de usuario asociado a la credencial."""
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value

    @property
    def password_hash(self) -> str:
        """Devuelve el hash de la contraseña."""
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value: str) -> None:
        self._password_hash = value

    @property
    def usuario_id(self) -> str:
        """Devuelve el identificador del usuario relacionado."""
        return self._usuario_id

    @usuario_id.setter
    def usuario_id(self, value: str) -> None:
        self._usuario_id = value

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la credencial a un diccionario."""
        return {
            "username": self._username,
            "password_hash": self._password_hash,
            "usuario_id": self._usuario_id,
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Crea una instancia de Credencial desde un diccionario."""
        return cls(
            username=data.get("username", ""),
            password_hash=data.get("password_hash", ""),
            usuario_id=data.get("usuario_id", ""),
        )

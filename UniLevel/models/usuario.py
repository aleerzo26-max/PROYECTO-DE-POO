from __future__ import annotations

from typing import Any, Dict, Type, TypeVar

from models.persona import Persona

T = TypeVar("T", bound="Usuario")


class Usuario(Persona):
    """Clase que representa a un usuario del sistema UniLevel."""

    def __init__(
        self,
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        telefono: str,
        username: str,
        rol: str,
    ) -> None:
        super().__init__(nombre, apellido, documento, email, telefono)
        self._username = username
        self._rol = rol

    @property
    def username(self) -> str:
        """Devuelve el nombre de usuario."""
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value

    @property
    def rol(self) -> str:
        """Devuelve el rol asignado al usuario."""
        return self._rol

    @rol.setter
    def rol(self, value: str) -> None:
        self._rol = value

    def get_role(self) -> str:
        """Devuelve el rol funcional del usuario."""
        return self._rol

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el usuario a un diccionario para almacenamiento."""
        payload = super().to_dict()
        payload.update({
            "username": self._username,
            "rol": self._rol,
        })
        return payload

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Crea una instancia de Usuario desde un diccionario."""
        return cls(
            nombre=data.get("nombre", ""),
            apellido=data.get("apellido", ""),
            documento=data.get("documento", ""),
            email=data.get("email", ""),
            telefono=data.get("telefono", ""),
            username=data.get("username", ""),
            rol=data.get("rol", ""),
        )

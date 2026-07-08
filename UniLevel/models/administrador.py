from __future__ import annotations

from typing import Any, Dict, Type, TypeVar

from models.usuario import Usuario

T = TypeVar("T", bound="Administrador")


class Administrador(Usuario):
    """Modelo de administrador con permisos de gestión del sistema."""

    def __init__(
        self,
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        telefono: str,
        username: str,
        rol: str,
        permisos: list[str] | None = None,
    ) -> None:
        super().__init__(nombre, apellido, documento, email, telefono, username, rol)
        self._permisos = permisos or []

    @property
    def permisos(self) -> list[str]:
        """Devuelve la lista de permisos del administrador."""
        return self._permisos

    @permisos.setter
    def permisos(self, value: list[str]) -> None:
        self._permisos = value

    def gestionar_sistema(self) -> None:
        """Placeholder para acciones de gestión del sistema."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el administrador a un diccionario."""
        payload = super().to_dict()
        payload.update({"permisos": self._permisos})
        return payload

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Crea una instancia de Administrador desde un diccionario."""
        return cls(
            nombre=data.get("nombre", ""),
            apellido=data.get("apellido", ""),
            documento=data.get("documento", ""),
            email=data.get("email", ""),
            telefono=data.get("telefono", ""),
            username=data.get("username", ""),
            rol=data.get("rol", ""),
            permisos=data.get("permisos", []),
        )

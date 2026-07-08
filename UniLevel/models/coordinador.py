from __future__ import annotations

from typing import Any, Dict, Type, TypeVar

from models.usuario import Usuario

T = TypeVar("T", bound="Coordinador")


class Coordinador(Usuario):
    """Modelo de coordinador con responsabilidades en el proceso de nivelación."""

    def __init__(
        self,
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        telefono: str,
        username: str,
        rol: str,
        dependencia: str,
        facultad: str,
    ) -> None:
        super().__init__(nombre, apellido, documento, email, telefono, username, rol)
        self._dependencia = dependencia
        self._facultad = facultad

    @property
    def dependencia(self) -> str:
        """Devuelve la dependencia académica del coordinador."""
        return self._dependencia

    @dependencia.setter
    def dependencia(self, value: str) -> None:
        self._dependencia = value

    @property
    def facultad(self) -> str:
        """Devuelve la facultad asociada al coordinador."""
        return self._facultad

    @facultad.setter
    def facultad(self, value: str) -> None:
        self._facultad = value

    def coordinar_programa(self) -> None:
        """Placeholder para la acción de coordinar el programa de nivelación."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el coordinador a un diccionario."""
        payload = super().to_dict()
        payload.update({
            "dependencia": self._dependencia,
            "facultad": self._facultad,
        })
        return payload

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Crea una instancia de Coordinador desde un diccionario."""
        return cls(
            nombre=data.get("nombre", ""),
            apellido=data.get("apellido", ""),
            documento=data.get("documento", ""),
            email=data.get("email", ""),
            telefono=data.get("telefono", ""),
            username=data.get("username", ""),
            rol=data.get("rol", ""),
            dependencia=data.get("dependencia", ""),
            facultad=data.get("facultad", ""),
        )

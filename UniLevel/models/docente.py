from __future__ import annotations

from typing import Any, Dict, Type, TypeVar

from models.usuario import Usuario

T = TypeVar("T", bound="Docente")


class Docente(Usuario):
    """Modelo de docente con información académica y de enseñanza."""

    def __init__(
        self,
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        telefono: str,
        username: str,
        rol: str,
        titulo: str,
        departamento: str,
    ) -> None:
        super().__init__(nombre, apellido, documento, email, telefono, username, rol)
        self._titulo = titulo
        self._departamento = departamento

    @property
    def titulo(self) -> str:
        """Devuelve el título profesional del docente."""
        return self._titulo

    @titulo.setter
    def titulo(self, value: str) -> None:
        self._titulo = value

    @property
    def departamento(self) -> str:
        """Devuelve el departamento académico del docente."""
        return self._departamento

    @departamento.setter
    def departamento(self, value: str) -> None:
        self._departamento = value

    def asignar_evaluacion(self) -> None:
        """Placeholder para la acción de asignar evaluaciones."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el docente a un diccionario."""
        payload = super().to_dict()
        payload.update({
            "titulo": self._titulo,
            "departamento": self._departamento,
        })
        return payload

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Crea una instancia de Docente desde un diccionario."""
        return cls(
            nombre=data.get("nombre", ""),
            apellido=data.get("apellido", ""),
            documento=data.get("documento", ""),
            email=data.get("email", ""),
            telefono=data.get("telefono", ""),
            username=data.get("username", ""),
            rol=data.get("rol", ""),
            titulo=data.get("titulo", ""),
            departamento=data.get("departamento", ""),
        )

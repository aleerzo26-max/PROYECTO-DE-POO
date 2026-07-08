from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T", bound="Persona")


class Persona(ABC):
    """Clase base para todas las personas del sistema UniLevel."""

    def __init__(
        self,
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        telefono: str,
    ) -> None:
        self._nombre = nombre
        self._apellido = apellido
        self._documento = documento
        self._email = email
        self._telefono = telefono

    @property
    def nombre(self) -> str:
        """Devuelve el nombre de la persona."""
        return self._nombre

    @nombre.setter
    def nombre(self, value: str) -> None:
        self._nombre = value

    @property
    def apellido(self) -> str:
        """Devuelve el apellido de la persona."""
        return self._apellido

    @apellido.setter
    def apellido(self, value: str) -> None:
        self._apellido = value

    @property
    def documento(self) -> str:
        """Devuelve el documento de identidad de la persona."""
        return self._documento

    @documento.setter
    def documento(self, value: str) -> None:
        self._documento = value

    @property
    def email(self) -> str:
        """Devuelve el correo electrónico de la persona."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = value

    @property
    def telefono(self) -> str:
        """Devuelve el teléfono de la persona."""
        return self._telefono

    @telefono.setter
    def telefono(self, value: str) -> None:
        self._telefono = value

    @abstractmethod
    def get_role(self) -> str:
        """Devuelve el rol de la persona dentro del sistema."""
        raise NotImplementedError()

    def to_dict(self) -> Dict[str, Any]:
        """Serializa los atributos básicos de la persona."""
        return {
            "nombre": self._nombre,
            "apellido": self._apellido,
            "documento": self._documento,
            "email": self._email,
            "telefono": self._telefono,
        }

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Crea una instancia desde un diccionario.

        Esta implementación debe ser provista por cada subclase.
        """
        raise NotImplementedError("from_dict debe implementarse en la subclase")

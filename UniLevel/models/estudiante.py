from __future__ import annotations

from typing import Any, Dict, Type, TypeVar

from models.usuario import Usuario

T = TypeVar("T", bound="Estudiante")


class Estudiante(Usuario):
    """Modelo de estudiante con información académica y de carrera."""

    def __init__(
        self,
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        telefono: str,
        username: str,
        rol: str,
        codigo_estudiante: str,
        carrera: str,
        semestre: int,
    ) -> None:
        super().__init__(nombre, apellido, documento, email, telefono, username, rol)
        self._codigo_estudiante = codigo_estudiante
        self._carrera = carrera
        self._semestre = semestre

    @property
    def codigo_estudiante(self) -> str:
        """Devuelve el código académico del estudiante."""
        return self._codigo_estudiante

    @codigo_estudiante.setter
    def codigo_estudiante(self, value: str) -> None:
        self._codigo_estudiante = value

    @property
    def carrera(self) -> str:
        """Devuelve la carrera registrada para el estudiante."""
        return self._carrera

    @carrera.setter
    def carrera(self, value: str) -> None:
        self._carrera = value

    @property
    def semestre(self) -> int:
        """Devuelve el semestre actual del estudiante."""
        return self._semestre

    @semestre.setter
    def semestre(self, value: int) -> None:
        self._semestre = value

    def consultar_matricula(self) -> None:
        """Placeholder para la acción de consultar matrícula del estudiante."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el estudiante a un diccionario."""
        payload = super().to_dict()
        payload.update({
            "codigo_estudiante": self._codigo_estudiante,
            "carrera": self._carrera,
            "semestre": self._semestre,
        })
        return payload

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Crea una instancia de Estudiante desde un diccionario."""
        return cls(
            nombre=data.get("nombre", ""),
            apellido=data.get("apellido", ""),
            documento=data.get("documento", ""),
            email=data.get("email", ""),
            telefono=data.get("telefono", ""),
            username=data.get("username", ""),
            rol=data.get("rol", ""),
            codigo_estudiante=data.get("codigo_estudiante", ""),
            carrera=data.get("carrera", ""),
            semestre=data.get("semestre", 0),
        )

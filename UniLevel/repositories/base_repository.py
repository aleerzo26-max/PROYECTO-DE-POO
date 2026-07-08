from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from utils.json_manager import JsonManager


class BaseRepository(ABC):
    """Clase base para repositorios que persisten datos en archivos JSON.

    Esta clase centraliza la ruta del archivo JSON y los métodos CRUD básicos.
    Los repositorios concretos deben implementar la conversión de objetos.
    """

    def __init__(self, ruta_archivo: str) -> None:
        self._ruta_archivo = ruta_archivo
        self._json_manager = JsonManager()

    @abstractmethod
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los elementos del repositorio."""
        raise NotImplementedError()

    @abstractmethod
    def obtener_por_id(self, id: Any) -> Dict[str, Any] | None:
        """Obtiene un elemento por su identificador."""
        raise NotImplementedError()

    @abstractmethod
    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda un nuevo objeto en el repositorio."""
        raise NotImplementedError()

    @abstractmethod
    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        """Actualiza un objeto existente identificado por su id."""
        raise NotImplementedError()

    @abstractmethod
    def eliminar(self, id: Any) -> bool:
        """Elimina un objeto identificado por su id."""
        raise NotImplementedError()

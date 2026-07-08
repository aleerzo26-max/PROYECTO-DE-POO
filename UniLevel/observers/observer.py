from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Observer(ABC):
    """Interfaz base para los observadores del patrón Observer.

    UniLevel usa este patrón porque los procesos del negocio se disparan
    a partir de eventos como la creación de usuarios, matrículas, tareas y
    calificaciones. Observer permite separar el origen del evento de las
    reacciones secundarias, manteniendo el sistema más extensible y limpio.
    """

    @abstractmethod
    def update(self, evento: str, datos: Any) -> None:
        """Recibe un evento emitido por el sujeto y ejecuta la lógica asociada."""
        raise NotImplementedError

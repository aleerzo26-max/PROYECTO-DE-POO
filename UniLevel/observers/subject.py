from __future__ import annotations

from typing import Any, List

try:
    from observers.observer import Observer
except ImportError:
    from UniLevel.observers.observer import Observer


class Subject:
    """Sujeto encargado de publicar eventos y notificar a los observadores.

    Antes de Observer, este tipo de lógica estaba mezclada con las operaciones
    de negocio. Ahora el Subject concentra la emisión de eventos y deja que
    los observadores reaccionen sin acoplarse al flujo principal.
    """

    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def agregar_observer(self, observer: Observer) -> None:
        """Registra un observador para recibir notificaciones."""
        if observer not in self._observers:
            self._observers.append(observer)

    def eliminar_observer(self, observer: Observer) -> None:
        """Elimina un observador de la lista de notificaciones."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notificar(self, evento: str, datos: Any) -> None:
        """Notifica a todos los observadores registrados sobre un evento."""
        for observer in self._observers:
            try:
                observer.update(evento, datos)
            except Exception:
                continue

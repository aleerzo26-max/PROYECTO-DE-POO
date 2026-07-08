from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from werkzeug.datastructures import FileStorage


class IImportador(ABC):
    """Interfaz que define el contrato para servicios de importación de datos."""

    @abstractmethod
    def procesar_archivo(self, archivo: FileStorage) -> Dict[str, Any]:
        """Procesa un archivo de importación y retorna estadísticas."""
        raise NotImplementedError()

    @abstractmethod
    def generar_template_csv(self) -> str:
        """Genera un template CSV para importación."""
        raise NotImplementedError()

    @abstractmethod
    def generar_template_xlsx(self) -> bytes:
        """Genera un template XLSX para importación."""
        raise NotImplementedError()

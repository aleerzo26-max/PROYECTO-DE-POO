from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class IReporte(ABC):
    """Interfaz que define la contracto para servicios de reporte."""

    @abstractmethod
    def listar_reportes(self) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    @abstractmethod
    def obtener_reporte(self, reporte_id: Any) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def generar_reporte_estadisticas(self, usuario_id: Any, formato: str = "csv", criterios: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def descargar_reporte(self, reporte_id: Any) -> Tuple[bytes, str, str]:
        raise NotImplementedError()

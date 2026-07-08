from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.periodo_academico_repository import PeriodoAcademicoRepository


class PeriodoAcademicoService:
    """Servicio responsable de la gestión de periodos académicos."""

    def __init__(self, periodo_repository: PeriodoAcademicoRepository) -> None:
        self._periodo_repository = periodo_repository

    def listar_periodos(self) -> List[Dict[str, Any]]:
        return self._periodo_repository.obtener_todos()

    def obtener_periodo_por_id(self, periodo_id: Any) -> Optional[Dict[str, Any]]:
        return self._periodo_repository.obtener_por_id(periodo_id)

    def obtener_periodo_activo(self) -> Optional[Dict[str, Any]]:
        """Retorna el periodo académico activo configurado en el sistema."""
        periodos = self.listar_periodos()
        for periodo in periodos:
            if not isinstance(periodo, dict):
                continue
            if periodo.get("activo") is True:
                return periodo
            if str(periodo.get("estado", "")).lower() == "activo":
                return periodo
        return None

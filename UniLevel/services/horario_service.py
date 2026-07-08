from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from repositories.horario_repository import HorarioRepository


class HorarioService:
    """Servicio responsable de la planificación y consulta de horarios académicos."""

    def __init__(self, horario_repository: HorarioRepository) -> None:
        self._horario_repository = horario_repository

    def generar_horario(self, matricula: Dict[str, Any], paralelo: Dict[str, Any]) -> Dict[str, Any]:
        """Genera y guarda un horario asociado a una matrícula."""
        horario = {
            "id": str(uuid.uuid4()),
            "matricula_id": matricula["id"],
            "estudiante_id": matricula["estudiante_id"],
            "paralelo_id": matricula["paralelo_id"],
            "asignatura": paralelo.get("asignatura", ""),
            "docente_id": paralelo.get("docente_id"),
            "periodo_academico": matricula.get("periodo_academico", ""),
            "descripcion": (
                f"Horario asignado para {paralelo.get('asignatura', 'curso')} "
                f"(paralelo {paralelo.get('nombre', 'sin paralelo')})"
            ),
            "estado": "activo",
        }
        return self._horario_repository.guardar(horario)

    def listar_horarios(self) -> List[Dict[str, Any]]:
        """Devuelve todos los horarios registrados."""
        return self._horario_repository.obtener_todos()

    def obtener_por_matricula(self, matricula_id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene el horario asociado a una matrícula."""
        return self._horario_repository.obtener_por_matricula(matricula_id)

    def cancelar_horario_por_matricula(self, matricula_id: Any) -> bool:
        """Marca como cancelado el horario asociado a una matrícula."""
        horario = self.obtener_por_matricula(matricula_id)
        if horario is None:
            return False
        return self._horario_repository.actualizar(horario["id"], {"estado": "cancelado"})

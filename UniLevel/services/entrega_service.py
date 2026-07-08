from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from repositories.entrega_repository import EntregaRepository
from repositories.matricula_repository import MatriculaRepository
from repositories.tarea_repository import TareaRepository
from services.notificacion_service import NotificacionService


class EntregaService:
    """Servicio responsable de la gestión de entregas de tareas."""

    def __init__(
        self,
        entrega_repository: EntregaRepository,
        tarea_repository: TareaRepository,
        matricula_repository: MatriculaRepository,
        notificacion_service: NotificacionService,
    ) -> None:
        self._entrega_repository = entrega_repository
        self._tarea_repository = tarea_repository
        self._matricula_repository = matricula_repository
        self._notificacion_service = notificacion_service

    def listar_por_tarea(self, tarea_id: Any) -> List[Dict[str, Any]]:
        """Lista las entregas asociadas a una tarea."""
        return self._entrega_repository.buscar_por_tarea(tarea_id)

    def listar_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Lista las entregas que ha realizado un estudiante."""
        return self._entrega_repository.buscar_por_estudiante(estudiante_id)

    def obtener_entrega(self, entrega_id: Any) -> Dict[str, Any]:
        """Obtiene una entrega por su identificador."""
        entrega = self._entrega_repository.obtener_por_id(entrega_id)
        if entrega is None:
            raise ValueError("Entrega no encontrada.")
        return entrega

    def obtener_entrega_por_tarea_y_estudiante(self, tarea_id: Any, estudiante_id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene la entrega de un estudiante para una tarea específica."""
        return self._entrega_repository.buscar_por_tarea_y_estudiante(tarea_id, estudiante_id)

    def registrar_entrega(
        self,
        tarea_id: Any,
        estudiante_id: Any,
        nombre_archivo: str,
        comentario: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Registra o actualiza la entrega de un estudiante para una tarea."""
        tarea = self._tarea_repository.obtener_por_id(tarea_id)
        if tarea is None:
            raise ValueError("Tarea no encontrada.")

        if not self._estudiante_matriculado_en_paralelo(estudiante_id, tarea.get("paralelo_id")):
            raise PermissionError("El estudiante no está matriculado en el paralelo de esta tarea.")

        self._validar_entrega_a_tiempo(tarea.get("fecha_entrega"))

        entrega_existente = self._entrega_repository.buscar_por_tarea_y_estudiante(tarea_id, estudiante_id)
        entrega_data = {
            "tarea_id": tarea_id,
            "estudiante_id": estudiante_id,
            "fecha_entrega": datetime.utcnow().isoformat(),
            "archivo": nombre_archivo,
            "comentario": comentario or "",
            "estado": "entregado",
            "puntuacion": None,
            "comentario_docente": "",
        }

        if entrega_existente is not None:
            self._entrega_repository.actualizar(entrega_existente["id"], entrega_data)
            entrega = self._entrega_repository.obtener_por_id(entrega_existente["id"])
        else:
            entrega = self._entrega_repository.guardar({"id": datetime.utcnow().timestamp().__str__(), **entrega_data})

        if tarea.get("docente_id"):
            self._notificacion_service.crear_notificacion(
                tarea["docente_id"],
                "Nueva entrega de tarea",
                f"El estudiante ha entregado la tarea '{tarea.get('titulo')}'.",
            )

        return entrega

    def calificar_entrega(
        self,
        entrega_id: Any,
        docente_id: Any,
        puntuacion: float,
        comentario: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Califica una entrega si el docente corresponde a la tarea."""
        entrega = self.obtener_entrega(entrega_id)
        tarea = self._tarea_repository.obtener_por_id(entrega.get("tarea_id"))
        if tarea is None:
            raise ValueError("Tarea asociada no encontrada.")

        if tarea.get("docente_id") != docente_id:
            raise PermissionError("Solo el docente a cargo puede calificar esta entrega.")

        if puntuacion < 0 or puntuacion > 10:
            raise ValueError("La puntuación debe estar entre 0 y 10.")

        actualizacion: Dict[str, Any] = {
            "puntuacion": puntuacion,
            "comentario_docente": comentario or "",
            "estado": "calificada",
            "fecha_calificacion": datetime.utcnow().isoformat(),
        }

        actualizado = self._entrega_repository.actualizar(entrega_id, actualizacion)
        if not actualizado:
            raise RuntimeError("No fue posible calificar la entrega.")

        entrega_calificada = self._entrega_repository.obtener_por_id(entrega_id)
        if entrega_calificada and entrega_calificada.get("estudiante_id"):
            self._notificacion_service.crear_notificacion(
                entrega_calificada["estudiante_id"],
                "Entrega calificada",
                f"Tu entrega de la tarea '{tarea.get('titulo')}' ha sido calificada con {puntuacion}.",
            )

        return entrega_calificada

    def _estudiante_matriculado_en_paralelo(self, estudiante_id: Any, paralelo_id: Any) -> bool:
        matriculas = self._matricula_repository.buscar_por_estudiante(estudiante_id)
        return any(
            isinstance(matricula, dict)
            and matricula.get("paralelo_id") == paralelo_id
            and str(matricula.get("estado", "")).lower() == "matriculado"
            for matricula in matriculas
        )

    def _validar_entrega_a_tiempo(self, fecha_entrega: Optional[str]) -> None:
        if fecha_entrega is None:
            raise ValueError("La tarea no tiene fecha de entrega definida.")

        try:
            fecha_limite = datetime.fromisoformat(fecha_entrega).date()
        except ValueError as error:
            raise ValueError("La fecha de entrega de la tarea es inválida.") from error

        if datetime.utcnow().date() > fecha_limite:
            raise ValueError("La fecha límite ya ha pasado. No se aceptan entregas tardías.")

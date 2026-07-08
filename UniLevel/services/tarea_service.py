from __future__ import annotations

from datetime import datetime
import uuid
from typing import Any, Dict, List, Optional

from repositories.matricula_repository import MatriculaRepository
from repositories.paralelo_repository import ParaleloRepository
from repositories.tarea_repository import TareaRepository
from services.notificacion_service import NotificacionService


class TareaService:
    """Servicio responsable de la gestión de tareas académicas."""

    def __init__(
        self,
        tarea_repository: TareaRepository,
        paralelo_repository: ParaleloRepository,
        matricula_repository: MatriculaRepository,
        notificacion_service: NotificacionService,
    ) -> None:
        self._tarea_repository = tarea_repository
        self._paralelo_repository = paralelo_repository
        self._matricula_repository = matricula_repository
        self._notificacion_service = notificacion_service

    def listar_por_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        """Lista las tareas creadas por un docente."""
        tareas = self._tarea_repository.buscar_por_docente(docente_id)
        return sorted(tareas, key=lambda tarea: tarea.get("fecha_entrega", ""))

    def listar_por_paralelo(self, paralelo_id: Any) -> List[Dict[str, Any]]:
        """Lista las tareas de un paralelo."""
        return self._tarea_repository.buscar_por_paralelo(paralelo_id)

    def obtener_tarea(self, tarea_id: Any) -> Dict[str, Any]:
        """Obtiene una tarea por su identificador."""
        tarea = self._tarea_repository.obtener_por_id(tarea_id)
        if tarea is None:
            raise ValueError("Tarea no encontrada.")
        return tarea

    def listar_tareas_para_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Lista las tareas de los paralelos donde está matriculado el estudiante."""
        matriculas = [
            matricula
            for matricula in self._matricula_repository.buscar_por_estudiante(estudiante_id)
            if isinstance(matricula, dict) and str(matricula.get("estado", "")).lower() == "matriculado"
        ]

        paralelo_ids = {matricula.get("paralelo_id") for matricula in matriculas if matricula.get("paralelo_id")}
        tareas = []
        for paralelo_id in paralelo_ids:
            tareas.extend(self._tarea_repository.buscar_por_paralelo(paralelo_id))

        return sorted(tareas, key=lambda tarea: tarea.get("fecha_entrega", ""))

    def crear_tarea(self, datos: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        """Crea una nueva tarea si el docente está asignado al paralelo."""
        self._validar_datos_tarea(datos)

        paralelo = self._obtener_paralelo(datos["paralelo_id"])
        if paralelo.get("docente_id") != docente_id:
            raise PermissionError("Solo el docente asignado a este paralelo puede crear tareas.")

        fecha_entrega = self._parsear_fecha_entrega(datos["fecha_entrega"])
        if fecha_entrega <= datetime.utcnow().date():
            raise ValueError("La fecha de entrega debe ser una fecha futura válida.")

        tarea = {
            "id": str(uuid.uuid4()),
            "titulo": datos["titulo"].strip(),
            "descripcion": datos["descripcion"].strip(),
            "paralelo_id": datos["paralelo_id"],
            "docente_id": docente_id,
            "fecha_creacion": datetime.utcnow().isoformat(),
            "fecha_entrega": fecha_entrega.isoformat(),
            "estado": "publicada",
            "archivo_instrucciones": datos.get("archivo_instrucciones", ""),
        }

        tarea_guardada = self._tarea_repository.guardar(tarea)
        self._notificar_estudiantes_paralelo(paralelo, tarea_guardada)
        return tarea_guardada

    def editar_tarea(self, tarea_id: Any, datos: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        """Edita una tarea existente si el docente es el autor."""
        tarea = self.obtener_tarea(tarea_id)
        if tarea.get("docente_id") != docente_id:
            raise PermissionError("Solo el docente creador puede editar esta tarea.")

        actualizacion: Dict[str, Any] = {}
        if "titulo" in datos and datos["titulo"]:
            actualizacion["titulo"] = datos["titulo"].strip()
        if "descripcion" in datos and datos["descripcion"]:
            actualizacion["descripcion"] = datos["descripcion"].strip()
        if "fecha_entrega" in datos and datos["fecha_entrega"]:
            fecha_entrega = self._parsear_fecha_entrega(datos["fecha_entrega"])
            if fecha_entrega <= datetime.utcnow().date():
                raise ValueError("La fecha de entrega debe ser una fecha futura válida.")
            actualizacion["fecha_entrega"] = fecha_entrega.isoformat()

        if not actualizacion:
            return tarea

        actualizado = self._tarea_repository.actualizar(tarea_id, actualizacion)
        if not actualizado:
            raise RuntimeError("No fue posible editar la tarea.")

        return self.obtener_tarea(tarea_id)

    def eliminar_tarea(self, tarea_id: Any, docente_id: Any) -> bool:
        """Elimina una tarea si el docente creador lo solicita."""
        tarea = self.obtener_tarea(tarea_id)
        if tarea.get("docente_id") != docente_id:
            raise PermissionError("Solo el docente creador puede eliminar esta tarea.")
        return self._tarea_repository.eliminar(tarea_id)

    def _validar_datos_tarea(self, datos: Dict[str, Any]) -> None:
        """Valida los campos requeridos para una tarea."""
        if not datos.get("titulo"):
            raise ValueError("El título de la tarea es obligatorio.")
        if not datos.get("descripcion"):
            raise ValueError("La descripción de la tarea es obligatoria.")
        if not datos.get("paralelo_id"):
            raise ValueError("El paralelo de la tarea es obligatorio.")
        if not datos.get("fecha_entrega"):
            raise ValueError("La fecha de entrega de la tarea es obligatoria.")

    def _obtener_paralelo(self, paralelo_id: Any) -> Dict[str, Any]:
        paralelo = self._paralelo_repository.obtener_por_id(paralelo_id)
        if paralelo is None:
            raise ValueError("Paralelo no encontrado.")
        return paralelo

    def _parsear_fecha_entrega(self, fecha_str: str) -> datetime.date:
        try:
            fecha_entrega = datetime.fromisoformat(fecha_str)
            return fecha_entrega.date()
        except ValueError as error:
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.") from error

    def _notificar_estudiantes_paralelo(self, paralelo: Dict[str, Any], tarea: Dict[str, Any]) -> None:
        matriculas = self._matricula_repository.buscar_por_paralelo(paralelo.get("id"))
        for matricula in matriculas:
            if not isinstance(matricula, dict) or str(matricula.get("estado", "")).lower() != "matriculado":
                continue
            self._notificacion_service.crear_notificacion(
                matricula["estudiante_id"],
                "Nueva tarea publicada",
                f"Se ha publicado la tarea '{tarea.get('titulo')}' para el paralelo {paralelo.get('nombre')}.",
            )

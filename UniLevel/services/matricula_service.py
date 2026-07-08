from __future__ import annotations

from datetime import datetime
import uuid
from typing import Any, Dict, List, Optional

from repositories.matricula_repository import MatriculaRepository
from repositories.paralelo_repository import ParaleloRepository
from services.horario_service import HorarioService
from services.notificacion_service import NotificacionService
from services.periodo_academico_service import PeriodoAcademicoService


class MatriculaService:
    """Servicio responsable de la gestión de matrículas en UniLevel."""

    def __init__(
        self,
        matricula_repository: MatriculaRepository,
        paralelo_repository: ParaleloRepository,
        horario_service: HorarioService,
        notificacion_service: NotificacionService,
        periodo_service: PeriodoAcademicoService,
    ) -> None:
        self._matricula_repository = matricula_repository
        self._paralelo_repository = paralelo_repository
        self._horario_service = horario_service
        self._notificacion_service = notificacion_service
        self._periodo_service = periodo_service

    def matricular_estudiante(
        self,
        estudiante_id: Any,
        paralelo_id: Any,
        datos_extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Matricula a un estudiante en un paralelo si el cupo lo permite.

        Esta operación realiza las validaciones de cupo y existencia de periodo activo,
        guarda la matrícula, crea el horario y genera una notificación automática.
        """
        if self._estudiante_ya_matriculado(estudiante_id, paralelo_id):
            raise ValueError("El estudiante ya está matriculado en este paralelo.")

        if not self.verificar_cupo(paralelo_id):
            raise ValueError("No existe cupo disponible en el paralelo.")

        periodo_activo = self._periodo_service.obtener_periodo_activo()
        if periodo_activo is None:
            raise ValueError("No existe un período académico activo para realizar la matrícula.")

        paralelo = self._obtener_paralelo(paralelo_id)
        fecha_matricula = datetime.now().isoformat()

        matricula = {
            "id": str(uuid.uuid4()),
            "estudiante_id": estudiante_id,
            "paralelo_id": paralelo_id,
            "fecha_matricula": fecha_matricula,
            "periodo_academico": periodo_activo.get("nombre", ""),
            "estado": "Matriculado",
        }

        if datos_extra:
            extras_filtrados = {k: v for k, v in datos_extra.items() if k != "periodo_academico"}
            matricula.update(extras_filtrados)

        matricula_guardada = self._matricula_repository.guardar(matricula)

        try:
            horario_generado = self._horario_service.generar_horario(matricula_guardada, paralelo)
        except Exception as error:
            self._matricula_repository.eliminar(matricula_guardada["id"])
            raise RuntimeError(
                "No se pudo generar el horario de la matrícula. La matrícula ha sido revertida."
            ) from error

        if horario_generado is None:
            self._matricula_repository.eliminar(matricula_guardada["id"])
            raise RuntimeError("No se pudo generar el horario de la matrícula.")

        self._notificacion_service.crear_notificacion(
            estudiante_id,
            "Matrícula Exitosa",
            "Has sido matriculado exitosamente en el curso de nivelación. Revisa tu horario y las asignaturas asignadas.",
        )

        self._notificacion_service.crear_notificacion(
            estudiante_id,
            "Horario Disponible",
            "Tu horario de clases ya se encuentra disponible en el sistema. Ingresa a tu perfil para consultar las asignaturas, horarios y paralelos asignados.",
        )

        return matricula_guardada

    def cancelar_matricula(self, matricula_id: Any) -> bool:
        """Cancela una matrícula y marca el horario como cancelado."""
        matricula = self._matricula_repository.obtener_por_id(matricula_id)
        if matricula is None:
            raise ValueError("Matrícula no encontrada.")

        if matricula.get("estado") == "cancelado":
            raise ValueError("La matrícula ya está cancelada.")

        self._horario_service.cancelar_horario_por_matricula(matricula_id)

        actualizado = self._matricula_repository.actualizar(
            matricula_id,
            {
                "estado": "cancelado",
                "fecha_cancelacion": datetime.utcnow().isoformat(),
            },
        )

        if actualizado:
            self._notificacion_service.crear_notificacion(
                matricula["estudiante_id"],
                "Matrícula cancelada",
                "Su matrícula ha sido cancelada y el horario asociado ha sido desactivado.",
            )

        return actualizado

    def verificar_cupo(self, paralelo_id: Any) -> bool:
        """Valida si el paralelo tiene cupo disponible."""
        paralelo = self._obtener_paralelo(paralelo_id)
        cupo_maximo = paralelo.get("capacidad_maxima")
        if cupo_maximo is None:
            raise ValueError("El paralelo no tiene capacidad definida.")

        matriculas_paralelo = [
            matricula
            for matricula in self._matricula_repository.buscar_por_paralelo(paralelo_id)
            if isinstance(matricula, dict) and str(matricula.get("estado", "")).lower() == "matriculado"
        ]
        return len(matriculas_paralelo) < int(cupo_maximo)

    def asignar_paralelo(self, estudiante_id: Any, paralelo_id: Any) -> Dict[str, Any]:
        """Asigna un paralelo a un estudiante nuevo o existente, respetando cupo y duplicados."""
        if self._estudiante_ya_matriculado(estudiante_id, paralelo_id):
            raise ValueError("El estudiante ya está asignado a este paralelo.")

        if not self.verificar_cupo(paralelo_id):
            raise ValueError("No existe cupo disponible en el paralelo.")

        matriculas_estudiante = self._matricula_repository.buscar_por_estudiante(estudiante_id)
        paralelo = self._obtener_paralelo(paralelo_id)

        if matriculas_estudiante:
            matricula_existente = matriculas_estudiante[0]
            self._horario_service.cancelar_horario_por_matricula(matricula_existente["id"])
            actualizado = self._matricula_repository.actualizar(
                matricula_existente["id"],
                {"paralelo_id": paralelo_id, "periodo_academico": matricula_existente.get("periodo_academico", "")},
            )
            if actualizado:
                matricula_actualizada = self._matricula_repository.obtener_por_id(matricula_existente["id"])
                if matricula_actualizada is not None:
                    self._horario_service.generar_horario(matricula_actualizada, paralelo)
                    self._notificacion_service.crear_notificacion(
                        estudiante_id,
                        "Cambio de paralelo",
                        f"Su matrícula se ha reasignado al paralelo {paralelo.get('nombre', '')} de {paralelo.get('asignatura', '')}.",
                    )
                return {"actualizado": True}
            return {"actualizado": False}

        return self.matricular_estudiante(estudiante_id, paralelo_id)

    def listar_matriculas(self) -> List[Dict[str, Any]]:
        """Lista todas las matrículas registradas."""
        return self._matricula_repository.obtener_todos()

    def listar_matriculas_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Devuelve todas las matrículas (incluidas no activas) de un estudiante."""
        return self._matricula_repository.buscar_por_estudiante(estudiante_id)

    def obtener_matricula_activa_por_estudiante(self, estudiante_id: Any) -> Optional[Dict[str, Any]]:
        """Devuelve la matrícula activa (estado 'Matriculado') de un estudiante, si existe."""
        for m in self._matricula_repository.buscar_por_estudiante(estudiante_id):
            if isinstance(m, dict) and str(m.get("estado", "")).lower() == "matriculado":
                return m
        return None

    def obtener_matricula_por_id(self, matricula_id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene una matrícula por su identificador."""
        return self._matricula_repository.obtener_por_id(matricula_id)

    def _estudiante_ya_matriculado(self, estudiante_id: Any, paralelo_id: Any) -> bool:
        """Verifica si el estudiante ya está matriculado en el paralelo indicado."""
        return any(
            isinstance(matricula, dict)
            and matricula.get("paralelo_id") == paralelo_id
            and str(matricula.get("estado", "")).lower() == "matriculado"
            for matricula in self._matricula_repository.buscar_por_estudiante(estudiante_id)
        )

    def _obtener_paralelo(self, paralelo_id: Any) -> Dict[str, Any]:
        """Recupera un paralelo existente o lanza error si no existe."""
        paralelo = self._paralelo_repository.obtener_por_id(paralelo_id)
        if paralelo is None:
            raise ValueError("Paralelo no encontrado.")
        return paralelo

    def eliminar_matriculas_por_estudiante(self, estudiante_id: Any) -> int:
        """Elimina permanentemente todas las matrículas asociadas a un estudiante.

        Devuelve el número de matrículas eliminadas.
        """
        contador = 0
        matriculas = self._matricula_repository.buscar_por_estudiante(estudiante_id)
        for matricula in list(matriculas):
            if not isinstance(matricula, dict) or not matricula.get("id"):
                continue
            matricula_id = matricula["id"]
            try:
                # intentar cancelar horario asociado antes de eliminar
                try:
                    self._horario_service.cancelar_horario_por_matricula(matricula_id)
                except Exception:
                    pass

                if self._matricula_repository.eliminar(matricula_id):
                    contador += 1
            except Exception:
                continue

        return contador

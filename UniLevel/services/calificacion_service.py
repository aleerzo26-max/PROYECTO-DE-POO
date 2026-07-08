from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from repositories.calificacion_repository import CalificacionRepository
from repositories.matricula_repository import MatriculaRepository
from repositories.paralelo_repository import ParaleloRepository
from services.notificacion_service import NotificacionService


class CalificacionService:
    """Servicio responsable de la gestión de calificaciones académicas."""

    def __init__(
        self,
        calificacion_repository: CalificacionRepository,
        paralelo_repository: ParaleloRepository,
        matricula_repository: MatriculaRepository,
        notificacion_service: NotificacionService,
    ) -> None:
        self._calificacion_repository = calificacion_repository
        self._paralelo_repository = paralelo_repository
        self._matricula_repository = matricula_repository
        self._notificacion_service = notificacion_service

    def listar_por_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        """Lista las calificaciones registradas por un docente."""
        calificaciones = self._calificacion_repository.buscar_por_docente(docente_id)
        return sorted(calificaciones, key=lambda c: c.get("fecha_registro", ""), reverse=True)

    def listar_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Lista las calificaciones de un estudiante."""
        calificaciones = self._calificacion_repository.buscar_por_estudiante(estudiante_id)
        return sorted(calificaciones, key=lambda c: c.get("fecha_registro", ""), reverse=True)

    def obtener_calificacion(self, calificacion_id: Any) -> Dict[str, Any]:
        """Obtiene una calificación por su identificador."""
        calificacion = self._calificacion_repository.obtener_por_id(calificacion_id)
        if calificacion is None:
            raise ValueError("Calificación no encontrada.")
        return calificacion

    def registrar_calificacion(self, datos: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        """Registra una nueva calificación siempre que el docente sea el asignado."""
        self._validar_datos_calificacion(datos)

        paralelo = self._obtener_paralelo(datos["paralelo_id"])
        if paralelo.get("docente_id") != docente_id:
            raise PermissionError("Solo el docente asignado al paralelo puede registrar calificaciones.")

        if not self._estudiante_matriculado_en_paralelo(datos["estudiante_id"], paralelo.get("id")):
            raise PermissionError("El estudiante no está matriculado en el paralelo seleccionado.")

        nota = self._validar_nota(datos["nota"])

        calificacion = {
            "id": str(uuid.uuid4()),
            "estudiante_id": datos["estudiante_id"],
            "docente_id": docente_id,
            "paralelo_id": datos["paralelo_id"],
            "evaluacion": datos.get("evaluacion", "").strip(),
            "nota": nota,
            "comentario": datos.get("comentario", "").strip(),
            "fecha_registro": datetime.utcnow().isoformat(),
            "fecha_actualizacion": datetime.utcnow().isoformat(),
            "estado": "registrada",
        }

        calificacion_guardada = self._calificacion_repository.guardar(calificacion)
        self._notificar_estudiante_nueva_calificacion(calificacion_guardada)
        return calificacion_guardada

    def editar_calificacion(self, calificacion_id: Any, datos: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        """Edita una calificación existente, validando permiso del docente."""
        calificacion = self.obtener_calificacion(calificacion_id)
        paralelo = self._obtener_paralelo(calificacion.get("paralelo_id"))

        if paralelo.get("docente_id") != docente_id:
            raise PermissionError("Solo el docente asignado puede editar esta calificación.")

        actualizacion: Dict[str, Any] = {}
        if "nota" in datos and datos["nota"] is not None:
            actualizacion["nota"] = self._validar_nota(datos["nota"])
        if "evaluacion" in datos:
            actualizacion["evaluacion"] = datos.get("evaluacion", "").strip()
        if "comentario" in datos:
            actualizacion["comentario"] = datos.get("comentario", "").strip()

        if not actualizacion:
            return calificacion

        actualizacion["fecha_actualizacion"] = datetime.utcnow().isoformat()
        actualizado = self._calificacion_repository.actualizar(calificacion_id, {**calificacion, **actualizacion})
        if not actualizado:
            raise RuntimeError("No fue posible editar la calificación.")

        calificacion_actualizada = self.obtener_calificacion(calificacion_id)
        self._notificar_estudiante_calificacion_actualizada(calificacion_actualizada)
        return calificacion_actualizada

    def calcular_promedio_estudiante(self, estudiante_id: Any) -> float:
        """Calcula el promedio de todas las calificaciones de un estudiante."""
        calificaciones = self._calificacion_repository.buscar_por_estudiante(estudiante_id)
        notas = [calificacion.get("nota") for calificacion in calificaciones if isinstance(calificacion.get("nota"), (int, float))]
        if not notas:
            return 0.0
        return round(sum(notas) / len(notas), 2)

    def listar_todas_calificaciones(self) -> List[Dict[str, Any]]:
        """Lista todas las calificaciones del sistema."""
        return self._calificacion_repository.obtener_todos()

    def calcular_tasa_aprobacion(self) -> float:
        """Calcula la tasa de aprobación global basada en las calificaciones registradas."""
        calificaciones = self.listar_todas_calificaciones()
        notas_validas = [
            calificacion.get("nota")
            for calificacion in calificaciones
            if isinstance(calificacion.get("nota"), (int, float))
        ]
        if not notas_validas:
            return 0.0
        aprobadas = [nota for nota in notas_validas if nota >= 7]
        tasa = (len(aprobadas) / len(notas_validas)) * 100
        return round(tasa, 2)

    def _validar_datos_calificacion(self, datos: Dict[str, Any]) -> None:
        if not datos.get("estudiante_id"):
            raise ValueError("El estudiante es obligatorio.")
        if not datos.get("paralelo_id"):
            raise ValueError("El paralelo es obligatorio.")
        if datos.get("nota") is None or datos.get("nota") == "":
            raise ValueError("La nota es obligatoria.")
        self._validar_nota(datos["nota"])

    def _validar_nota(self, nota: Any) -> float:
        try:
            nota_num = float(nota)
        except (TypeError, ValueError):
            raise ValueError("La nota debe ser un número entre 0 y 10.")
        if nota_num < 0 or nota_num > 10:
            raise ValueError("La nota debe estar entre 0 y 10.")
        return round(nota_num, 2)

    def _obtener_paralelo(self, paralelo_id: Any) -> Dict[str, Any]:
        paralelo = self._paralelo_repository.obtener_por_id(paralelo_id)
        if paralelo is None:
            raise ValueError("Paralelo no encontrado.")
        return paralelo

    def _estudiante_matriculado_en_paralelo(self, estudiante_id: Any, paralelo_id: Any) -> bool:
        matriculas = self._matricula_repository.buscar_por_estudiante(estudiante_id)
        return any(
            isinstance(matricula, dict)
            and matricula.get("paralelo_id") == paralelo_id
            and str(matricula.get("estado", "")).lower() == "matriculado"
            for matricula in matriculas
        )

    def _notificar_estudiante_nueva_calificacion(self, calificacion: Dict[str, Any]) -> None:
        if not calificacion.get("estudiante_id"):
            return
        self._notificacion_service.crear_notificacion(
            calificacion["estudiante_id"],
            "Nueva calificación registrada",
            f"Se ha registrado la calificación {calificacion.get('nota')} para '{calificacion.get('evaluacion') or 'evaluación'}'.",
        )

    def _notificar_estudiante_calificacion_actualizada(self, calificacion: Dict[str, Any]) -> None:
        if not calificacion.get("estudiante_id"):
            return
        self._notificacion_service.crear_notificacion(
            calificacion["estudiante_id"],
            "Calificación actualizada",
            f"Tu calificación para '{calificacion.get('evaluacion') or 'evaluación'}' ha sido actualizada a {calificacion.get('nota')}.",
        )

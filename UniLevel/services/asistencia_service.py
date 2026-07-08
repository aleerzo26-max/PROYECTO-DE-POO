from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from repositories.asistencia_repository import AsistenciaRepository
from repositories.matricula_repository import MatriculaRepository
from repositories.paralelo_repository import ParaleloRepository
from services.notificacion_service import NotificacionService

LIMITE_INASISTENCIAS = 3


class AsistenciaService:
    """Servicio para la gestión de asistencia de estudiantes."""

    def __init__(
        self,
        asistencia_repository: AsistenciaRepository,
        paralelo_repository: ParaleloRepository,
        matricula_repository: MatriculaRepository,
        notificacion_service: NotificacionService,
    ) -> None:
        self._asistencia_repository = asistencia_repository
        self._paralelo_repository = paralelo_repository
        self._matricula_repository = matricula_repository
        self._notificacion_service = notificacion_service

    def listar_por_docente(self, docente_id: Any, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Lista las asistencias registradas por un docente."""
        asistencias = self._asistencia_repository.buscar_por_docente(docente_id)

        if filtros is None:
            filtros = {}

        if filtros.get("paralelo_id"):
            asistencias = [
                asistencia
                for asistencia in asistencias
                if asistencia.get("paralelo_id") == filtros["paralelo_id"]
            ]

        if filtros.get("fecha"):
            asistencias = [
                asistencia
                for asistencia in asistencias
                if asistencia.get("fecha") == filtros["fecha"]
            ]

        return sorted(asistencias, key=lambda a: a.get("fecha", ""), reverse=True)

    def listar_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Lista las asistencias de un estudiante."""
        asistencias = self._asistencia_repository.buscar_por_estudiante(estudiante_id)
        return sorted(asistencias, key=lambda a: a.get("fecha", ""), reverse=True)

    def obtener_asistencia(self, asistencia_id: Any) -> Dict[str, Any]:
        """Obtiene un registro de asistencia por su identificador."""
        asistencia = self._asistencia_repository.obtener_por_id(asistencia_id)
        if asistencia is None:
            raise ValueError("Asistencia no encontrada.")
        return asistencia

    def registrar_asistencia(self, datos: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        """Registra una nueva asistencia para un estudiante en un paralelo."""
        self._validar_datos_asistencia(datos)

        paralelo = self._obtener_paralelo(datos["paralelo_id"])
        if paralelo.get("docente_id") != docente_id:
            raise PermissionError("Solo el docente asignado al paralelo puede registrar asistencias.")

        estudiante_id = datos["estudiante_id"]
        fecha = self._validar_fecha(datos["fecha"])

        if not self._estudiante_matriculado_en_paralelo(estudiante_id, paralelo.get("id")):
            raise PermissionError("El estudiante no está matriculado en el paralelo seleccionado.")

        self._validar_unico_registro(estudiante_id, fecha)
        asistio = self._parse_asistio(datos.get("asistio"))

        asistencia = {
            "id": str(uuid.uuid4()),
            "estudiante_id": estudiante_id,
            "docente_id": docente_id,
            "paralelo_id": datos["paralelo_id"],
            "fecha": fecha,
            "asistio": asistio,
            "estado": "Presente" if asistio else "Ausente",
            "comentario": datos.get("comentario", "").strip(),
            "fecha_registro": datetime.utcnow().isoformat(),
            "fecha_actualizacion": datetime.utcnow().isoformat(),
        }

        asistencia_guardada = self._asistencia_repository.guardar(asistencia)
        self._notificar_si_supera_limite(estudiante_id)
        return asistencia_guardada

    def editar_asistencia(self, asistencia_id: Any, datos: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        """Edita un registro de asistencia existente."""
        asistencia = self.obtener_asistencia(asistencia_id)
        paralelo = self._obtener_paralelo(asistencia.get("paralelo_id"))

        if paralelo.get("docente_id") != docente_id:
            raise PermissionError("Solo el docente asignado puede editar esta asistencia.")

        actualizacion: Dict[str, Any] = {}

        if datos.get("fecha"):
            fecha = self._validar_fecha(datos["fecha"])
            if fecha != asistencia.get("fecha"):
                self._validar_unico_registro(asistencia.get("estudiante_id"), fecha)
            actualizacion["fecha"] = fecha

        if "asistio" in datos and datos.get("asistio") is not None:
            asistio = self._parse_asistio(datos.get("asistio"))
            actualizacion["asistio"] = asistio
            actualizacion["estado"] = "Presente" if asistio else "Ausente"

        if "comentario" in datos:
            actualizacion["comentario"] = datos.get("comentario", "").strip()

        if not actualizacion:
            return asistencia

        actualizacion["fecha_actualizacion"] = datetime.utcnow().isoformat()
        actualizado = self._asistencia_repository.actualizar(asistencia_id, {**asistencia, **actualizacion})

        if not actualizado:
            raise RuntimeError("No fue posible editar la asistencia.")

        asistencia_actualizada = self.obtener_asistencia(asistencia_id)
        self._notificar_si_supera_limite(asistencia_actualizada.get("estudiante_id"))
        return asistencia_actualizada

    def calcular_porcentaje_asistencia_estudiante(self, estudiante_id: Any) -> float:
        """Calcula el porcentaje de asistencia de un estudiante."""
        asistencias = self._asistencia_repository.buscar_por_estudiante(estudiante_id)
        if not asistencias:
            return 0.0

        total = len(asistencias)
        presentes = sum(1 for asistencia in asistencias if asistencia.get("asistio") is True)
        return round((presentes / total) * 100, 2)

    def _validar_datos_asistencia(self, datos: Dict[str, Any]) -> None:
        if not datos.get("estudiante_id"):
            raise ValueError("El estudiante es obligatorio.")
        if not datos.get("paralelo_id"):
            raise ValueError("El paralelo es obligatorio.")
        if not datos.get("fecha"):
            raise ValueError("La fecha de asistencia es obligatoria.")
        if datos.get("asistio") is None or str(datos.get("asistio")).strip() == "":
            raise ValueError("Debe indicar si el estudiante asistió o no.")

    def _validar_fecha(self, fecha: str) -> str:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise ValueError("La fecha de asistencia debe tener el formato AAAA-MM-DD.")

        if fecha_obj > date.today():
            raise ValueError("No se permiten fechas futuras en el registro de asistencia.")

        return fecha_obj.isoformat()

    def _parse_asistio(self, valor: Any) -> bool:
        if isinstance(valor, bool):
            return valor

        valor_texto = str(valor).strip().lower()
        if valor_texto in {"1", "true", "si", "sí", "s", "presente", "asistio"}:
            return True
        if valor_texto in {"0", "false", "no", "n", "ausente", "falta", "inasistencia"}:
            return False

        raise ValueError("El valor de asistencia debe ser 'Presente' o 'Ausente'.")

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

    def _validar_unico_registro(self, estudiante_id: Any, fecha: str) -> None:
        registros = self._asistencia_repository.buscar_por_estudiante_y_fecha(estudiante_id, fecha)
        if registros:
            raise ValueError("Ya existe un registro de asistencia para este estudiante en la fecha indicada.")

    def _contar_inasistencias(self, estudiante_id: Any) -> int:
        asistencias = self._asistencia_repository.buscar_por_estudiante(estudiante_id)
        return sum(1 for asistencia in asistencias if asistencia.get("asistio") is False)

    def _notificar_si_supera_limite(self, estudiante_id: Any) -> None:
        inasistencias = self._contar_inasistencias(estudiante_id)
        if inasistencias > LIMITE_INASISTENCIAS:
            self._notificacion_service.crear_notificacion(
                estudiante_id,
                "Límite de inasistencias superado",
                f"Has acumulado {inasistencias} inasistencias. Por favor contacta a tu docente para regularizar tu situación.",
            )

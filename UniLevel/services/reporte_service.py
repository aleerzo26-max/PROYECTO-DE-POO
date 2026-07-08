from __future__ import annotations

import csv
import io
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from factories.reporte_factory import ReporteFactory
from repositories.calificacion_repository import CalificacionRepository
from repositories.asistencia_repository import AsistenciaRepository
from repositories.matricula_repository import MatriculaRepository
from repositories.paralelo_repository import ParaleloRepository
from repositories.periodo_academico_repository import PeriodoAcademicoRepository
from repositories.reporte_repository import ReporteRepository
from repositories.usuario_repository import UsuarioRepository


class ReporteService:
    """Servicio para la gestión de reportes académicos."""

    def __init__(
        self,
        reporte_repository: ReporteRepository,
        usuario_repository: UsuarioRepository,
        matricula_repository: MatriculaRepository,
        calificacion_repository: CalificacionRepository,
        asistencia_repository: AsistenciaRepository,
        paralelo_repository: ParaleloRepository,
        periodo_repository: PeriodoAcademicoRepository,
        carpeta_reportes: str,
    ) -> None:
        self._reporte_repository = reporte_repository
        self._usuario_repository = usuario_repository
        self._matricula_repository = matricula_repository
        self._calificacion_repository = calificacion_repository
        self._asistencia_repository = asistencia_repository
        self._paralelo_repository = paralelo_repository
        self._periodo_repository = periodo_repository
        self._carpeta_reportes = carpeta_reportes
        os.makedirs(self._carpeta_reportes, exist_ok=True)

    def listar_reportes(self) -> List[Dict[str, Any]]:
        reportes = self._reporte_repository.obtener_todos()
        return sorted(reportes, key=lambda r: r.get("fecha_generacion", ""), reverse=True)

    def obtener_reporte(self, reporte_id: Any) -> Dict[str, Any]:
        reporte = self._reporte_repository.obtener_por_id(reporte_id)
        if reporte is None:
            raise ValueError("Reporte no encontrado.")
        return reporte

    def generar_reporte_estadisticas(
        self,
        usuario_id: Any,
        formato: str = "csv",
        criterios: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        formato = formato.lower()
        if formato not in {"csv", "xlsx"}:
            raise ValueError("Formato de reporte no válido. Use 'csv' o 'xlsx'.")

        estadisticas = self._construir_estadisticas(criterios)
        archivo_bytes, nombre_archivo = ReporteFactory.generar_estadisticas(estadisticas, formato)
        ruta_archivo = self._guardar_archivo(nombre_archivo, archivo_bytes)

        reporte = {
            "id": str(uuid.uuid4()),
            "usuario_id": usuario_id,
            "tipo": "estadisticas",
            "formato": formato,
            "nombre_archivo": nombre_archivo,
            "ruta_archivo": ruta_archivo,
            "fecha_generacion": datetime.utcnow().isoformat(),
            "descripcion": "Reporte de estadísticas del sistema UniLevel.",
        }

        self._reporte_repository.guardar(reporte)

        return {
            "id": reporte["id"],
            "nombre": nombre_archivo,
            "archivo": archivo_bytes,
            "tipo_contenido": self._tipo_contenido(formato),
        }

    def descargar_reporte(self, reporte_id: Any) -> Tuple[bytes, str, str]:
        reporte = self.obtener_reporte(reporte_id)
        ruta = reporte.get("ruta_archivo")
        if not ruta or not os.path.exists(ruta):
            raise FileNotFoundError("El archivo del reporte no se encuentra en el servidor.")

        with open(ruta, "rb") as archivo:
            contenido = archivo.read()

        return contenido, reporte.get("nombre_archivo", "reporte"), self._tipo_contenido(reporte.get("formato", "csv"))

    def _construir_estadisticas(self, criterios: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        usuarios = self._usuario_repository.obtener_todos()
        matriculas = self._matricula_repository.obtener_todos()
        calificaciones = self._calificacion_repository.obtener_todos()
        asistencias = self._asistencia_repository.obtener_todos()
        paralelos = self._paralelo_repository.obtener_todos()
        periodos = self._periodo_repository.obtener_todos()

        total_estudiantes = len([u for u in usuarios if u.get("rol") == "estudiante"])
        total_docentes = len([u for u in usuarios if u.get("rol") == "docente"])
        total_administradores = len([u for u in usuarios if u.get("rol") == "administrador"])
        total_coordinadores = len([u for u in usuarios if u.get("rol") == "coordinador"])
        promedio_calificacion_global = self._calcular_promedio_global(calificaciones)
        porcentaje_asistencia_global = self._calcular_porcentaje_asistencia_global(asistencias)

        matriculas_por_paralelo: Dict[str, int] = {}
        for matricula in matriculas:
            paralelo_id = matricula.get("paralelo_id")
            if paralelo_id:
                matriculas_por_paralelo[paralelo_id] = matriculas_por_paralelo.get(paralelo_id, 0) + 1

        estadisticas_por_paralelo = []
        for paralelo in paralelos:
            paralelo_id = paralelo.get("id")
            estudiantes_inscritos = matriculas_por_paralelo.get(paralelo_id, 0)
            calificaciones_paralelo = [c for c in calificaciones if c.get("paralelo_id") == paralelo_id]
            asistencias_paralelo = [a for a in asistencias if a.get("paralelo_id") == paralelo_id]
            promedio_paralelo = self._calcular_promedio_global(calificaciones_paralelo)
            porcentaje_asistencia_paralelo = self._calcular_porcentaje_asistencia_global(asistencias_paralelo)
            estadisticas_por_paralelo.append(
                {
                    "paralelo_id": paralelo_id,
                    "nombre_paralelo": paralelo.get("nombre", "Sin nombre"),
                    "estudiantes_inscritos": estudiantes_inscritos,
                    "promedio_calificaciones": promedio_paralelo,
                    "porcentaje_asistencia": porcentaje_asistencia_paralelo,
                }
            )

        return {
            "totales": {
                "usuarios": len(usuarios),
                "estudiantes": total_estudiantes,
                "docentes": total_docentes,
                "administradores": total_administradores,
                "coordinadores": total_coordinadores,
                "matriculas": len(matriculas),
                "calificaciones": len(calificaciones),
                "asistencias": len(asistencias),
                "paralelos": len(paralelos),
                "promedio_calificacion_global": promedio_calificacion_global,
                "porcentaje_asistencia_global": porcentaje_asistencia_global,
                "periodos": len(periodos),
            },
            "por_paralelo": estadisticas_por_paralelo,
            "fecha_generacion": datetime.utcnow().isoformat(),
        }

    def _calcular_promedio_global(self, calificaciones: List[Dict[str, Any]]) -> float:
        notas = [float(c.get("nota", 0)) for c in calificaciones if c.get("nota") is not None]
        if not notas:
            return 0.0
        return round(sum(notas) / len(notas), 2)

    def _calcular_porcentaje_asistencia_global(self, asistencias: List[Dict[str, Any]]) -> float:
        if not asistencias:
            return 0.0
        total = len(asistencias)
        presentes = sum(1 for asistencia in asistencias if asistencia.get("asistio") is True)
        return round((presentes / total) * 100, 2)

    def _guardar_archivo(self, nombre_archivo: str, contenido: bytes) -> str:
        ruta = os.path.join(self._carpeta_reportes, nombre_archivo)
        with open(ruta, "wb") as archivo:
            archivo.write(contenido)
        return ruta

    def _tipo_contenido(self, formato: str) -> str:
        return (
            "text/csv"
            if formato == "csv"
            else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

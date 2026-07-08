from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Tuple


class ReporteFactory:
    """Fábrica de reportes y formatos de exportación."""

    @staticmethod
    def generar_estadisticas(datos: Dict[str, Any], formato: str = "csv") -> Tuple[bytes, str]:
        formato = formato.lower()
        nombre = f"reporte_estadisticas_{datos.get('fecha_generacion', '')[:10]}.{formato}"

        if formato == "csv":
            return ReporteFactory._generar_csv(datos), nombre
        if formato == "xlsx":
            return ReporteFactory._generar_xlsx(datos), nombre

        raise ValueError("Formato de reporte no soportado.")

    @staticmethod
    def _generar_csv(datos: Dict[str, Any]) -> bytes:
        salida = io.StringIO()
        escritor = csv.writer(salida)

        escritor.writerow(["Reporte de Estadísticas UniLevel"])
        escritor.writerow(["Generado el", datos.get("fecha_generacion", "")])
        escritor.writerow([])

        escritor.writerow(["Clave", "Valor"])
        for clave, valor in datos.get("totales", {}).items():
            escritor.writerow([clave, valor])

        escritor.writerow([])
        escritor.writerow(["Paralelo", "Estudiantes inscritos", "Promedio calificaciones", "Porcentaje asistencia"])
        for item in datos.get("por_paralelo", []):
            escritor.writerow([
                item.get("nombre_paralelo"),
                item.get("estudiantes_inscritos"),
                item.get("promedio_calificaciones"),
                item.get("porcentaje_asistencia"),
            ])

        return salida.getvalue().encode("utf-8")

    @staticmethod
    def _generar_xlsx(datos: Dict[str, Any]) -> bytes:
        try:
            import openpyxl
            from openpyxl.styles import Font
        except ImportError as error:
            raise ValueError("openpyxl no está instalado. Instálalo con: pip install openpyxl") from error

        workbook = openpyxl.Workbook()
        hoja_resumen = workbook.active
        hoja_resumen.title = "Resumen"

        hoja_resumen.append(["Reporte de Estadísticas UniLevel"])
        hoja_resumen.append(["Generado el", datos.get("fecha_generacion", "")])
        hoja_resumen.append([])

        hoja_resumen.append(["Clave", "Valor"])
        for clave, valor in datos.get("totales", {}).items():
            hoja_resumen.append([clave, valor])

        hoja_detalle = workbook.create_sheet("Por Paralelo")
        hoja_detalle.append(["Paralelo", "Estudiantes inscritos", "Promedio calificaciones", "Porcentaje asistencia"])
        for item in datos.get("por_paralelo", []):
            hoja_detalle.append(
                [
                    item.get("nombre_paralelo"),
                    item.get("estudiantes_inscritos"),
                    item.get("promedio_calificaciones"),
                    item.get("porcentaje_asistencia"),
                ]
            )

        for hoja in workbook.worksheets:
            for celda in hoja[1]:
                celda.font = Font(bold=True)

        buffer = io.BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

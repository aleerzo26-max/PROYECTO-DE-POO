"""Servicio de importación de usuarios.

Gestiona la lógica centralizada de validación y procesamiento de importaciones
mediante archivos CSV y XLSX.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from repositories.usuario_repository import UsuarioRepository
from repositories.notificacion_repository import NotificacionRepository
from utils.password_generator import PasswordGenerator
from utils.importador_usuarios import ImportadorUsuarios
from interfaces.i_importador import IImportador
from werkzeug.datastructures import FileStorage


class ImportadorService(IImportador):
    """Servicio de importación que coordina usuarios, notificaciones y validación."""

    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        notificacion_repository: NotificacionRepository,
        fachada: Any,
    ) -> None:
        """Inicializa el servicio con acceso a repositorios y fachada."""
        self._usuario_repository = usuario_repository
        self._notificacion_repository = notificacion_repository
        self._fachada = fachada
        self._password_gen = PasswordGenerator()
        self._importador_utilidad = ImportadorUsuarios(fachada)

    def procesar_archivo(self, archivo: FileStorage) -> Dict[str, Any]:
        """Procesa un archivo de importación con validación mejorada."""
        try:
            resultado = self._importador_utilidad.procesar_archivo(archivo)
            resultado["fecha_procesamiento"] = datetime.utcnow().isoformat()
            resultado["archivo_nombre"] = archivo.filename
            return resultado
        except Exception as e:
            return {
                "exitosos": 0,
                "errores": 1,
                "errores_detalle": [str(e)],
                "fecha_procesamiento": datetime.utcnow().isoformat(),
                "archivo_nombre": archivo.filename,
            }

    def generar_template_csv(self) -> str:
        """Genera un template CSV para importación."""
        return self._importador_utilidad.generar_template_csv()

    def generar_template_xlsx(self) -> bytes:
        """Genera un template XLSX para importación."""
        return self._importador_utilidad.generar_template_xlsx()

    def obtener_estadisticas_importacion(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        """Construye estadísticas formateadas a partir del resultado de importación."""
        exitosos = resultado.get("exitosos", 0)
        errores = resultado.get("errores", 0)
        total = exitosos + errores
        porcentaje_exito = round((exitosos / total * 100), 2) if total > 0 else 0

        return {
            "total": total,
            "exitosos": exitosos,
            "errores": errores,
            "porcentaje_exito": porcentaje_exito,
            "porcentaje_error": round(100 - porcentaje_exito, 2),
            "errores_detalle": resultado.get("errores_detalle", []),
            "fecha": resultado.get("fecha_procesamiento", ""),
            "archivo": resultado.get("archivo_nombre", ""),
        }

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

try:
    from observers.observer import Observer
    from utils.json_manager import JsonManager
except ImportError:
    from UniLevel.observers.observer import Observer
    from UniLevel.utils.json_manager import JsonManager


class AuditoriaObserver(Observer):
    """Observador que persiste registros de auditoría en el archivo JSON del sistema."""

    def __init__(self, auditoria_path: str) -> None:
        self._auditoria_path = auditoria_path

    def update(self, evento: str, datos: Any) -> None:
        descripcion = self._generar_detalle(evento, datos)
        registro: Dict[str, Any] = {
            "fecha": datetime.utcnow().isoformat(),
            "evento": evento,
            "usuario": self._obtener_usuario(datos),
            "descripcion": descripcion,
            "detalle": descripcion,
        }
        try:
            JsonManager.agregar_elemento(self._auditoria_path, registro)
        except Exception:
            pass

    def _obtener_usuario(self, datos: Any) -> str:
        if not isinstance(datos, dict):
            return "Desconocido"

        usuario = datos.get("usuario")
        if isinstance(usuario, dict):
            return usuario.get("id") or usuario.get("email") or "Desconocido"

        if "estudiante_id" in datos:
            return datos.get("estudiante_id")
        if "docente_id" in datos:
            return datos.get("docente_id")
        if "paralelo" in datos and isinstance(datos["paralelo"], dict):
            return datos["paralelo"].get("docente_id") or "Desconocido"
        return "Desconocido"

    def _generar_detalle(self, evento: str, datos: Any) -> str:
        if not isinstance(datos, dict):
            return "Evento registrado sin datos adicionales."

        if evento == "usuario_creado":
            usuario = datos.get("usuario")
            if isinstance(usuario, dict):
                return f"Nuevo usuario creado: {usuario.get('nombre', '')} {usuario.get('apellido', '')}."

        if evento == "estudiante_matriculado":
            matricula = datos.get("matricula")
            if isinstance(matricula, dict):
                return f"Estudiante {matricula.get('estudiante_id', '')} matriculado en paralelo {matricula.get('paralelo_id', '')}."

        if evento == "tarea_creada":
            tarea = datos.get("tarea")
            if isinstance(tarea, dict):
                return f"Tarea creada: {tarea.get('titulo', '')} para el paralelo {tarea.get('paralelo_id', '')}."

        if evento == "calificacion_publicada":
            calificacion = datos.get("calificacion")
            if isinstance(calificacion, dict):
                return f"Calificación publicada: {calificacion.get('nota', '')} para estudiante {calificacion.get('estudiante_id', '')}."

        if evento == "docente_asignado":
            paralelo = datos.get("paralelo")
            if isinstance(paralelo, dict):
                return f"Docente {paralelo.get('docente_id', '')} asignado al paralelo {paralelo.get('curso_nombre', paralelo.get('nombre', ''))}."

        return "Evento registrado con datos adicionales."

"""Ejemplo previo al patrón Observer.

Este archivo muestra cómo el proceso de creación de usuario estaba acoplado
antes de introducir el patrón. El método tenía la responsabilidad de:
- crear el usuario,
- crear una notificación interna,
- preparar el correo,
- registrar auditoría.

Ese acoplamiento dificultaba escalar el sistema cuando aparecían nuevos eventos.
"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict


class UsuarioServiceSinObserver:
    """Versión inicial con responsabilidades mezcladas."""

    def __init__(self) -> None:
        self._base_dir = Path(__file__).resolve().parent.parent
        self._notificaciones_path = self._base_dir / "data" / "notificaciones.json"
        self._auditoria_path = self._base_dir / "data" / "auditoria.json"

    def crear_usuario(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        # Antes de Observer, esta lógica hacía todo en un mismo lugar.
        usuario = {
            "id": "usuario-001",
            "nombre": datos["nombre"],
            "apellido": datos["apellido"],
            "email": datos["email"],
        }

        # 1) Crear notificación interna
        self._crear_notificacion(usuario)

        # 2) Preparar correo
        print("Correo preparado para enviar.")

        # 3) Registrar auditoría
        self._registrar_auditoria(usuario)
        return usuario

    def _crear_notificacion(self, usuario: Dict[str, Any]) -> None:
        registro = {
            "id": "notif-001",
            "usuario_id": usuario["id"],
            "titulo": "Cuenta creada",
            "mensaje": "Tu cuenta ha sido creada exitosamente.",
            "fecha": datetime.utcnow().isoformat(),
        }
        self._guardar_json(self._notificaciones_path, registro)

    def _registrar_auditoria(self, usuario: Dict[str, Any]) -> None:
        registro = {
            "fecha": datetime.utcnow().isoformat(),
            "evento": "usuario_creado",
            "usuario": usuario["id"],
            "descripcion": f"Usuario {usuario['nombre']} creado sin patrón Observer.",
        }
        self._guardar_json(self._auditoria_path, registro)

    def _guardar_json(self, ruta: Path, registro: Dict[str, Any]) -> None:
        if ruta.exists():
            with ruta.open("r", encoding="utf-8") as handle:
                datos = json.load(handle)
        else:
            datos = []
        if not isinstance(datos, list):
            datos = []
        datos.append(registro)
        with ruta.open("w", encoding="utf-8") as handle:
            json.dump(datos, handle, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    servicio = UsuarioServiceSinObserver()
    servicio.crear_usuario({"nombre": "Ana", "apellido": "López", "email": "ana@uni.com"})

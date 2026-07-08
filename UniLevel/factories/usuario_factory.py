from __future__ import annotations

from typing import Any, Dict

from models.administrador import Administrador
from models.docente import Docente
from models.estudiante import Estudiante
from models.coordinador import Coordinador


class UsuarioFactory:
    """Fábrica de usuarios para crear instancias según el rol."""

    def crear_usuario(self, rol: str, datos: Dict[str, Any]) -> Any:
        """Crea un objeto de usuario según el rol especificado."""
        rol_normalizado = rol.strip().lower()

        if rol_normalizado == "administrador":
            return Administrador(
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                documento=datos["documento"],
                email=datos["email"],
                telefono=datos.get("telefono", ""),
                username=datos["username"],
                rol=rol,
                permisos=datos.get("permisos", []),
            )

        if rol_normalizado == "docente":
            return Docente(
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                documento=datos["documento"],
                email=datos["email"],
                telefono=datos.get("telefono", ""),
                username=datos["username"],
                rol=rol,
                titulo=datos.get("titulo", ""),
                departamento=datos.get("departamento", ""),
            )

        if rol_normalizado == "estudiante":
            return Estudiante(
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                documento=datos["documento"],
                email=datos["email"],
                telefono=datos.get("telefono", ""),
                username=datos["username"],
                rol=rol,
                codigo_estudiante=datos.get("codigo_estudiante", ""),
                carrera=datos.get("carrera", ""),
                semestre=int(datos.get("semestre", 0)),
            )

        if rol_normalizado == "coordinador":
            return Coordinador(
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                documento=datos["documento"],
                email=datos["email"],
                telefono=datos.get("telefono", ""),
                username=datos["username"],
                rol=rol,
                dependencia=datos.get("dependencia", ""),
                facultad=datos.get("facultad", ""),
            )

        raise ValueError(f"Rol de usuario desconocido: {rol}")

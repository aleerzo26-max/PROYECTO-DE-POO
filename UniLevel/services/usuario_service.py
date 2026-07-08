from __future__ import annotations

import hashlib
import uuid
from typing import Any, Dict, List, Optional

from repositories.usuario_repository import UsuarioRepository
from services.notificacion_service import NotificacionService
from utils.email_sender import EmailSender
from utils.password_generator import PasswordGenerator


class UsuarioService:
    """Servicio responsable de la gestión de usuarios en UniLevel."""

    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        notificacion_service: NotificacionService,
        password_generator: PasswordGenerator,
        email_sender: EmailSender,
        matricula_service: "MatriculaService" | None = None,
    ) -> None:
        self._usuario_repository = usuario_repository
        self._notificacion_service = notificacion_service
        self._password_generator = password_generator
        self._email_sender = email_sender
        self._matricula_service = matricula_service

    def crear_usuario(
        self,
        datos_usuario: Dict[str, Any],
        contrasena_temporal: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Crea un nuevo usuario con contraseña temporal y notificación inicial."""
        self._validar_usuario_unico(datos_usuario)

        usuario_id = self._generar_id()
        # Generar contraseña temporal de 8 caracteres si no se provee
        if contrasena_temporal is None:
            contrasena_temporal = self._password_generator.generar_contrasena_temporal(8)
        password_hash = self._hash_password(contrasena_temporal)

        usuario = {
            "id": usuario_id,
            "nombre": datos_usuario["nombre"],
            "apellido": datos_usuario["apellido"],
            "documento": datos_usuario["documento"],
            "email": datos_usuario["email"],
            "telefono": datos_usuario.get("telefono", ""),
            "username": datos_usuario.get("username", datos_usuario["email"]),
            "rol": datos_usuario["rol"],
            "password_hash": password_hash,
            "password_temporal": True,
            "primer_inicio": True,
        }

        usuario_guardado = self._usuario_repository.guardar_usuario(usuario)

        notificacion = self._notificacion_service.crear_notificacion(
            usuario_id=usuario_id,
            titulo="Cuenta creada en UniLevel",
            mensaje=(
                "Su cuenta ha sido creada exitosamente. "
                "Utilice la contraseña temporal y cambie su contraseña en el primer inicio de sesión."
            ),
        )

        # Preparar envío de correo (estructura preparada, envío real opcional)
        self._email_sender.preparar_envio(
            destinatario=usuario["email"],
            asunto="Bienvenido a UniLevel",
            cuerpo=(
                f"Hola {usuario['nombre']},\n\n"
                f"Su cuenta en UniLevel ha sido creada con éxito.\n"
                f"Usuario: {usuario['username']}\n"
                f"Contraseña temporal: {contrasena_temporal}\n\n"
                "Recuerde cambiar su contraseña en el primer inicio de sesión."
            ),
        )

        # Retornar también la contraseña temporal para mostrarla al administrador
        return {
            "usuario": usuario_guardado,
            "notificacion": notificacion,
            "contrasena_temporal": contrasena_temporal,
        }

    def editar_usuario(self, usuario_id: Any, datos_actualizar: Dict[str, Any]) -> bool:
        """Edita los datos de un usuario existente."""
        usuario_existente = self.buscar_usuario(usuario_id)
        if usuario_existente is None:
            raise ValueError("Usuario no encontrado.")

        if "documento" in datos_actualizar and datos_actualizar["documento"] != usuario_existente.get("documento"):
            self._validar_cedula_unica(datos_actualizar["documento"], usuario_id)

        if "email" in datos_actualizar and datos_actualizar["email"] != usuario_existente.get("email"):
            self._validar_correo_unico(datos_actualizar["email"], usuario_id)

        return self._usuario_repository.actualizar(usuario_id, datos_actualizar)

    def eliminar_usuario(self, usuario_id: Any) -> bool:
        """Elimina un usuario del sistema (borrado permanente).

        También elimina referencias relacionadas (notificaciones y matrículas)
        cuando los servicios correspondientes están disponibles.
        """
        usuario = self.buscar_usuario(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado.")

        # Eliminar notificaciones del usuario
        if self._notificacion_service is not None:
            try:
                notificaciones = self._notificacion_service.listar_por_usuario(usuario_id)
                for noti in notificaciones:
                    try:
                        self._notificacion_service.eliminar_notificacion(noti.get("id"), usuario_id)
                    except Exception:
                        # no interrumpir la eliminación por errores en notificaciones
                        pass
            except Exception:
                pass

        # Eliminar matrículas asociadas (si el servicio está disponible)
        if getattr(self, "_matricula_service", None) is not None:
            try:
                # MatriculaService expone eliminar_matriculas_por_estudiante
                self._matricula_service.eliminar_matriculas_por_estudiante(usuario_id)
            except Exception:
                pass

        # Eliminar usuario definitivamente del repositorio
        return self._usuario_repository.eliminar(usuario_id)

    def activar_usuario(self, usuario_id: Any) -> bool:
        """Activa un usuario del sistema."""
        usuario = self.buscar_usuario(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado.")
        return self._usuario_repository.actualizar(usuario_id, {"activo": True})

    def desactivar_usuario(self, usuario_id: Any) -> bool:
        """Desactiva un usuario del sistema."""
        usuario = self.buscar_usuario(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado.")
        return self._usuario_repository.actualizar(usuario_id, {"activo": False})

    def cambiar_password(self, usuario_id: Any, nueva_password: str) -> bool:
        """Cambia la contraseña de un usuario."""
        usuario = self.buscar_usuario(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado.")
        
        if len(nueva_password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        
        password_hash = self._hash_password(nueva_password)
        return self._usuario_repository.actualizar(usuario_id, {
            "password_hash": password_hash,
            "password_temporal": False,
            "primer_inicio": False
        })

    def buscar_usuario(self, usuario_id: Any) -> Optional[Dict[str, Any]]:
        """Busca un usuario por su identificador."""
        return self._usuario_repository.obtener_por_id(usuario_id)

    def listar_usuarios(self) -> List[Dict[str, Any]]:
        """Lista todos los usuarios registrados (incluido eliminados)."""
        return self._usuario_repository.obtener_todos()

    def listar_usuarios_activos(self) -> List[Dict[str, Any]]:
        """Lista todos los usuarios activos."""
        return [u for u in self._usuario_repository.obtener_todos() 
                if u.get("activo", True) and not u.get("eliminado", False)]

    def listar_por_rol(self, rol: str) -> List[Dict[str, Any]]:
        """Lista los usuarios que pertenecen a un rol específico."""
        return self._usuario_repository.listar_por_rol(rol)

    def buscar_usuarios(self, criterio: str, valor: str) -> List[Dict[str, Any]]:
        """Busca usuarios por criterio (nombre, email, documento, rol)."""
        return self._usuario_repository.buscar_por_criterio(criterio, valor)

    def filtrar_usuarios(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filtra usuarios según múltiples criterios."""
        return self._usuario_repository.filtrar(filtros)

    def _validar_usuario_unico(self, datos_usuario: Dict[str, Any]) -> None:
        """Valida que la cédula y el correo no estén duplicados."""
        self._validar_cedula_unica(datos_usuario["documento"])
        self._validar_correo_unico(datos_usuario["email"])

    def _validar_cedula_unica(self, documento: str, usuario_id: Any = None) -> None:
        """Valida que no exista otro usuario con la misma cédula."""
        usuario = self._usuario_repository.buscar_por_cedula(documento)
        if usuario and usuario.get("id") != usuario_id:
            raise ValueError("Ya existe un usuario con la misma cédula.")

    def _validar_correo_unico(self, correo: str, usuario_id: Any = None) -> None:
        """Valida que no exista otro usuario con el mismo correo."""
        usuario = self._usuario_repository.buscar_por_correo(correo)
        if usuario and usuario.get("id") != usuario_id:
            raise ValueError("Ya existe un usuario con el mismo correo.")

    @staticmethod
    def _hash_password(password: str) -> str:
        """Genera un hash seguro para la contraseña."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _generar_id() -> str:
        """Genera un identificador único para un nuevo usuario."""
        return str(uuid.uuid4())

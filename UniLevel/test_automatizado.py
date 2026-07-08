"""
test_automatizado.py - Pruebas automatizadas del sistema UniLevel.

Este script prueba automáticamente las funcionalidades principales del sistema
sin intervención del usuario.
"""

import sys
import traceback
from pathlib import Path

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from UniLevel.repositories.usuario_repository import UsuarioRepository
from UniLevel.repositories.matricula_repository import MatriculaRepository
from UniLevel.repositories.paralelo_repository import ParaleloRepository
from UniLevel.repositories.notificacion_repository import NotificacionRepository
from UniLevel.repositories.periodo_academico_repository import PeriodoAcademicoRepository
from UniLevel.repositories.horario_repository import HorarioRepository
from UniLevel.services.autenticacion_service import AutenticacionService
from UniLevel.services.usuario_service import UsuarioService
from UniLevel.services.notificacion_service import NotificacionService
from UniLevel.services.matricula_service import MatriculaService
from UniLevel.services.horario_service import HorarioService
from UniLevel.services.periodo_academico_service import PeriodoAcademicoService
from UniLevel.services.paralelo_service import ParaleloService
from UniLevel.utils.password_generator import PasswordGenerator
from UniLevel.utils.email_sender import EmailSender
from UniLevel.facades.sistema_nivelacion_facade import SistemaNivelacionFacade


class PruebasAutomaticas:
    """Ejecuta pruebas automatizadas del sistema."""

    def __init__(self):
        """Inicializa los componentes del sistema."""
        self.ruta_base = Path(__file__).parent / "data"
        self.ruta_base.mkdir(exist_ok=True)

        # Repositorios
        self.usuario_repo = UsuarioRepository(str(self.ruta_base / "test_usuarios.json"))
        self.matricula_repo = MatriculaRepository(str(self.ruta_base / "test_matriculas.json"))
        self.paralelo_repo = ParaleloRepository(str(self.ruta_base / "test_paralelos.json"))
        self.notificacion_repo = NotificacionRepository(str(self.ruta_base / "test_notificaciones.json"))
        self.periodo_repo = PeriodoAcademicoRepository(str(self.ruta_base / "test_periodos.json"))
        self.horario_repo = HorarioRepository(str(self.ruta_base / "test_horarios.json"))

        # Servicios
        self.password_gen = PasswordGenerator()
        self.email_sender = EmailSender()
        self.notificacion_service = NotificacionService(self.notificacion_repo)
        self.horario_service = HorarioService(self.horario_repo)
        self.periodo_service = PeriodoAcademicoService(self.periodo_repo)
        self.paralelo_service = ParaleloService(self.paralelo_repo, self.matricula_repo)

        self.autenticacion_service = AutenticacionService(self.usuario_repo)
        self.usuario_service = UsuarioService(
            self.usuario_repo, self.notificacion_service, self.password_gen, self.email_sender
        )
        self.matricula_service = MatriculaService(
            self.matricula_repo,
            self.paralelo_repo,
            self.horario_service,
            self.notificacion_service,
            self.periodo_service,
        )

        # Fachada
        self.fachada = SistemaNivelacionFacade(
            self.autenticacion_service,
            self.usuario_service,
            self.matricula_service,
            self.paralelo_service,
            self.periodo_service,
            self.notificacion_service,
        )

        self.pruebas_exitosas = 0
        self.pruebas_fallidas = 0
        self.contraseña_temporal = None

    def _mostrar_prueba(self, nombre: str):
        """Muestra el inicio de una prueba."""
        print(f"\n{'=' * 60}")
        print(f"🧪 PRUEBA: {nombre}")
        print(f"{'=' * 60}")

    def _mostrar_exito(self, mensaje: str):
        """Muestra éxito."""
        print(f"✅ {mensaje}")
        self.pruebas_exitosas += 1

    def _mostrar_error(self, mensaje: str, excepcion: Exception = None):
        """Muestra error."""
        print(f"❌ {mensaje}")
        if excepcion:
            print(f"   Detalles: {str(excepcion)}")
        self.pruebas_fallidas += 1

    def prueba_crear_usuario(self):
        """Prueba: Crear un usuario."""
        self._mostrar_prueba("Crear usuario")
        try:
            datos = {
                "nombre": "Carlos",
                "apellido": "García",
                "documento": "9876543210",
                "email": "carlos@example.com",
                "telefono": "5559876543",
                "rol": "estudiante",
            }
            resultado = self.fachada.crear_usuario(datos)
            usuario_id = resultado["usuario"]["id"]
            self.contraseña_temporal = resultado["usuario"]["password_hash"]  # Solo para pruebas
            self._mostrar_exito(f"Usuario creado: {usuario_id}")
            return usuario_id
        except Exception as e:
            self._mostrar_error("Error creando usuario", e)
            return None

    def prueba_crear_docente(self):
        """Prueba: Crear un docente."""
        self._mostrar_prueba("Crear docente")
        try:
            datos = {
                "nombre": "Prof. Ana",
                "apellido": "López",
                "documento": "1111111111",
                "email": "ana@example.com",
                "telefono": "5551111111",
                "rol": "docente",
            }
            resultado = self.fachada.crear_usuario(datos)
            docente_id = resultado["usuario"]["id"]
            self._mostrar_exito(f"Docente creado: {docente_id}")
            return docente_id
        except Exception as e:
            self._mostrar_error("Error creando docente", e)
            return None

    def prueba_crear_paralelo(self, docente_id: str):
        """Prueba: Crear un paralelo."""
        self._mostrar_prueba("Crear paralelo")
        try:
            paralelo = {
                "nombre": "A",
                "asignatura": "Matemáticas",
                "docente_id": docente_id,
                "capacidad_maxima": 30,
            }
            resultado = self.paralelo_repo.guardar(paralelo)
            paralelo_id = resultado.get("id")
            self._mostrar_exito(f"Paralelo creado: {paralelo_id}")
            return paralelo_id
        except Exception as e:
            self._mostrar_error("Error creando paralelo", e)
            return None

    def prueba_matricular_estudiante(self, estudiante_id: str, paralelo_id: str):
        """Prueba: Matricular estudiante."""
        self._mostrar_prueba("Matricular estudiante")
        try:
            resultado = self.fachada.matricular_estudiante(estudiante_id, paralelo_id)
            self._mostrar_exito(f"Estudiante matriculado correctamente")
        except Exception as e:
            self._mostrar_error("Error matriculando estudiante", e)

    def prueba_verificar_cupo(self, paralelo_id: str):
        """Prueba: Verificar cupo disponible."""
        self._mostrar_prueba("Verificar cupo disponible")
        try:
            tiene_cupo = self.matricula_service.verificar_cupo(paralelo_id)
            self._mostrar_exito(f"Cupo disponible: {tiene_cupo}")
        except Exception as e:
            self._mostrar_error("Error verificando cupo", e)

    def prueba_listar_usuarios(self):
        """Prueba: Listar usuarios."""
        self._mostrar_prueba("Listar usuarios")
        try:
            usuarios = self.fachada.listar_usuarios()
            self._mostrar_exito(f"Usuarios encontrados: {len(usuarios)}")
            for usuario in usuarios:
                print(f"  - {usuario['nombre']} {usuario['apellido']} ({usuario['rol']})")
        except Exception as e:
            self._mostrar_error("Error listando usuarios", e)

    def prueba_listar_estudiantes(self):
        """Prueba: Listar estudiantes."""
        self._mostrar_prueba("Listar estudiantes")
        try:
            estudiantes = self.fachada.listar_estudiantes()
            self._mostrar_exito(f"Estudiantes encontrados: {len(estudiantes)}")
        except Exception as e:
            self._mostrar_error("Error listando estudiantes", e)

    def prueba_editar_usuario(self, usuario_id: str):
        """Prueba: Editar usuario."""
        self._mostrar_prueba("Editar usuario")
        try:
            datos = {"telefono": "9999999999"}
            resultado = self.fachada.editar_usuario(usuario_id, datos)
            self._mostrar_exito(f"Usuario editado correctamente")
        except Exception as e:
            self._mostrar_error("Error editando usuario", e)

    def prueba_usuario_duplicado(self):
        """Prueba: Intentar crear usuario duplicado (debe fallar)."""
        self._mostrar_prueba("Intentar crear usuario duplicado (debe fallar)")
        try:
            datos = {
                "nombre": "Carlos",
                "apellido": "García",
                "documento": "9876543210",  # Mismo documento
                "email": "otro@example.com",
                "telefono": "5559876543",
                "rol": "estudiante",
            }
            self.fachada.crear_usuario(datos)
            self._mostrar_error("Debería haber fallado pero no lo hizo")
        except ValueError as e:
            self._mostrar_exito(f"Validación correcta: {str(e)}")
        except Exception as e:
            self._mostrar_error("Error inesperado", e)

    def prueba_cambiar_password(self, usuario_id: str):
        """Prueba: Cambiar contraseña."""
        self._mostrar_prueba("Cambiar contraseña")
        try:
            resultado = self.autenticacion_service.cambiar_password(usuario_id, "nueva_contraseña_123")
            self._mostrar_exito(f"Contraseña cambiaracter correctamente")
        except Exception as e:
            self._mostrar_error("Error cambiando contraseña", e)

    def ejecutar_todas_las_pruebas(self):
        """Ejecuta todas las pruebas."""
        print("\n" + "=" * 60)
        print("🚀 INICIANDO PRUEBAS AUTOMATIZADAS DEL SISTEMA UNILEVEL")
        print("=" * 60)

        # Pruebas de usuario
        usuario_id = self.prueba_crear_usuario()
        docente_id = self.prueba_crear_docente()
        paralelo_id = self.prueba_crear_paralelo(docente_id)

        if usuario_id and paralelo_id:
            self.prueba_matricular_estudiante(usuario_id, paralelo_id)
            self.prueba_verificar_cupo(paralelo_id)
            self.prueba_editar_usuario(usuario_id)

        # Pruebas de listado
        self.prueba_listar_usuarios()
        self.prueba_listar_estudiantes()

        # Pruebas de validación
        self.prueba_usuario_duplicado()

        if usuario_id:
            self.prueba_cambiar_password(usuario_id)

        # Resumen
        self._mostrar_resumen()

    def _mostrar_resumen(self):
        """Muestra el resumen de pruebas."""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)
        print(f"✅ Pruebas exitosas: {self.pruebas_exitosas}")
        print(f"❌ Pruebas fallidas: {self.pruebas_fallidas}")
        total = self.pruebas_exitosas + self.pruebas_fallidas
        porcentaje = (self.pruebas_exitosas / total * 100) if total > 0 else 0
        print(f"📈 Porcentaje de éxito: {porcentaje:.1f}%")
        print("=" * 60)

        if self.pruebas_fallidas == 0:
            print("\n🎉 ¡Todas las pruebas pasaron correctamente!")
        else:
            print(f"\n⚠️  {self.pruebas_fallidas} prueba(s) fallaron. Revisar detalles arriba.")


if __name__ == "__main__":
    try:
        pruebas = PruebasAutomaticas()
        pruebas.ejecutar_todas_las_pruebas()
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        traceback.print_exc()

"""
main.py - Archivo de prueba para validar la arquitectura del sistema UniLevel.

Este archivo prueba la arquitectura completa del sistema antes de integrar Flask.
Realiza pruebas de los repositorios, servicios y la fachada desde consola.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Inicializar inyección de dependencias y componentes
from UniLevel.repositories.usuario_repository import UsuarioRepository
from UniLevel.repositories.matricula_repository import MatriculaRepository
from UniLevel.repositories.paralelo_repository import ParaleloRepository
from UniLevel.repositories.tarea_repository import TareaRepository
from UniLevel.repositories.calificacion_repository import CalificacionRepository
from UniLevel.repositories.asistencia_repository import AsistenciaRepository
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
from UniLevel.utils.json_manager import JsonManager
from UniLevel.utils.password_generator import PasswordGenerator
from UniLevel.utils.email_sender import EmailSender
from UniLevel.facades.sistema_nivelacion_facade import SistemaNivelacionFacade


class TestadorSistema:
    """Clase para pruebas interactivas del sistema UniLevel."""

    def __init__(self):
        """Inicializa todos los componentes del sistema."""
        self._inicializar_rutas()
        self._inicializar_repositorios()
        self._inicializar_servicios()
        self._inicializar_fachada()
        self._usuario_autenticado = None

    def _inicializar_rutas(self):
        """Configura las rutas de los archivos JSON."""
        self.ruta_base = Path(__file__).parent / "data"
        self.ruta_base.mkdir(exist_ok=True)

        self.rutas = {
            "usuarios": str(self.ruta_base / "usuarios.json"),
            "matriculas": str(self.ruta_base / "matriculas.json"),
            "paralelos": str(self.ruta_base / "paralelos.json"),
            "tareas": str(self.ruta_base / "tareas.json"),
            "calificaciones": str(self.ruta_base / "calificaciones.json"),
            "asistencias": str(self.ruta_base / "asistencias.json"),
            "notificaciones": str(self.ruta_base / "notificaciones.json"),
            "periodos": str(self.ruta_base / "periodos.json"),
            "horarios": str(self.ruta_base / "horarios.json"),
        }

    def _inicializar_repositorios(self):
        """Inicializa todos los repositorios."""
        self.usuario_repo = UsuarioRepository(self.rutas["usuarios"])
        self.matricula_repo = MatriculaRepository(self.rutas["matriculas"])
        self.paralelo_repo = ParaleloRepository(self.rutas["paralelos"])
        self.tarea_repo = TareaRepository(self.rutas["tareas"])
        self.calificacion_repo = CalificacionRepository(self.rutas["calificaciones"])
        self.asistencia_repo = AsistenciaRepository(self.rutas["asistencias"])

    def _inicializar_servicios(self):
        """Inicializa todos los servicios con inyección de dependencias."""
        self.password_gen = PasswordGenerator()
        self.email_sender = EmailSender()
        self.notificacion_repo = NotificacionRepository(self.rutas["notificaciones"])
        self.periodo_repo = PeriodoAcademicoRepository(self.rutas["periodos"])

        self.notificacion_service = NotificacionService(self.notificacion_repo)
        self.horario_repo = HorarioRepository(self.rutas["horarios"])
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

    def _inicializar_fachada(self):
        """Inicializa la fachada del sistema."""
        self.fachada = SistemaNivelacionFacade(
            self.autenticacion_service,
            self.usuario_service,
            self.matricula_service,
            self.paralelo_service,
            self.periodo_service,
            self.notificacion_service,
        )

    def mostrar_menu(self):
        """Muestra el menú principal de pruebas."""
        print("\n" + "=" * 50)
        print("     SISTEMA UNILEVEL - PRUEBAS DE ARQUITECTURA")
        print("=" * 50)
        print("1. Crear usuario")
        print("2. Iniciar sesión")
        print("3. Matricular estudiante")
        print("4. Crear paralelo")
        print("5. Crear tarea")
        print("6. Registrar calificación")
        print("7. Ver usuarios")
        print("8. Ver estudiantes")
        print("9. Ver docentes")
        print("10. Salir")
        print("=" * 50)

    def crear_usuario_interactivo(self):
        """Interfaz para crear un usuario."""
        print("\n--- CREAR USUARIO ---")
        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        documento = input("Documento (cédula): ").strip()
        email = input("Email: ").strip()
        telefono = input("Teléfono: ").strip()
        rol = input("Rol (administrador/docente/estudiante/coordinador): ").strip().lower()

        if rol not in ["administrador", "docente", "estudiante", "coordinador"]:
            self._mostrar_error("Rol no válido")
            return

        try:
            datos_usuario = {
                "nombre": nombre,
                "apellido": apellido,
                "documento": documento,
                "email": email,
                "telefono": telefono,
                "rol": rol,
            }
            resultado = self.fachada.crear_usuario(datos_usuario)
            self._mostrar_exito(f"Usuario creado: {resultado['usuario']['id']}")
        except ValueError as e:
            self._mostrar_error(str(e))
        except Exception as e:
            self._mostrar_error(f"Error inesperado: {str(e)}")

    def iniciar_sesion_interactivo(self):
        """Interfaz para iniciar sesión."""
        print("\n--- INICIAR SESIÓN ---")
        correo = input("Correo electrónico: ").strip()
        password = input("Contraseña: ").strip()

        try:
            usuario = self.fachada.iniciar_sesion(correo, password)
            self._usuario_autenticado = usuario
            self._mostrar_exito(f"Sesión iniciada como: {usuario.get('nombre')} {usuario.get('apellido')}")
        except RuntimeError as e:
            self._mostrar_error(str(e))
        except ValueError as e:
            self._mostrar_error(str(e))
        except Exception as e:
            self._mostrar_error(f"Error inesperado: {str(e)}")

    def matricular_estudiante_interactivo(self):
        """Interfaz para matricular un estudiante."""
        if not self._usuario_autenticado:
            self._mostrar_error("Debe iniciar sesión primero")
            return

        print("\n--- MATRICULAR ESTUDIANTE ---")
        estudiante_id = input("ID del estudiante: ").strip()
        paralelo_id = input("ID del paralelo: ").strip()

        try:
            resultado = self.fachada.matricular_estudiante(estudiante_id, paralelo_id)
            self._mostrar_exito(f"Estudiante matriculado correctamente")
        except ValueError as e:
            self._mostrar_error(str(e))
        except Exception as e:
            self._mostrar_error(f"Error inesperado: {str(e)}")

    def crear_paralelo_interactivo(self):
        """Interfaz para crear un paralelo."""
        print("\n--- CREAR PARALELO ---")
        nombre = input("Nombre del paralelo (ej: A, B, C): ").strip()
        asignatura = input("Nombre de la asignatura: ").strip()
        docente_id = input("ID del docente: ").strip()
        capacidad = input("Capacidad máxima: ").strip()

        try:
            capacidad = int(capacidad)
            paralelo = {
                "nombre": nombre,
                "asignatura": asignatura,
                "docente_id": docente_id,
                "capacidad_maxima": capacidad,
            }
            resultado = self.paralelo_repo.guardar(paralelo)
            self._mostrar_exito(f"Paralelo creado: {resultado.get('id')}")
        except ValueError:
            self._mostrar_error("Capacidad debe ser un número")
        except Exception as e:
            self._mostrar_error(f"Error inesperado: {str(e)}")

    def crear_tarea_interactivo(self):
        """Interfaz para crear una tarea."""
        print("\n--- CREAR TAREA ---")
        titulo = input("Título de la tarea: ").strip()
        descripcion = input("Descripción: ").strip()
        asignatura = input("Asignatura: ").strip()
        paralelo_id = input("ID del paralelo: ").strip()
        fecha_entrega = input("Fecha de entrega (YYYY-MM-DD): ").strip()

        try:
            tarea = {
                "titulo": titulo,
                "descripcion": descripcion,
                "asignatura": asignatura,
                "paralelo_id": paralelo_id,
                "fecha_entrega": fecha_entrega,
                "estado": "pendiente",
            }
            resultado = self.tarea_repo.guardar(tarea)
            self._mostrar_exito(f"Tarea creada: {resultado.get('id')}")
        except Exception as e:
            self._mostrar_error(f"Error inesperado: {str(e)}")

    def registrar_calificacion_interactivo(self):
        """Interfaz para registrar una calificación."""
        print("\n--- REGISTRAR CALIFICACIÓN ---")
        estudiante_id = input("ID del estudiante: ").strip()
        tarea_id = input("ID de la tarea: ").strip()
        puntuacion = input("Puntuación (0-10): ").strip()

        try:
            puntuacion = float(puntuacion)
            if puntuacion < 0 or puntuacion > 10:
                self._mostrar_error("Puntuación debe estar entre 0 y 10")
                return

            calificacion = {
                "estudiante_id": estudiante_id,
                "tarea_id": tarea_id,
                "puntuacion": puntuacion,
                "estado": "calificada",
            }
            resultado = self.calificacion_repo.guardar(calificacion)
            self._mostrar_exito(f"Calificación registrada: {resultado.get('id')}")
        except ValueError:
            self._mostrar_error("Puntuación debe ser un número")
        except Exception as e:
            self._mostrar_error(f"Error inesperado: {str(e)}")

    def ver_usuarios(self):
        """Muestra todos los usuarios registrados."""
        print("\n--- USUARIOS REGISTRADOS ---")
        try:
            usuarios = self.fachada.listar_usuarios()
            if not usuarios:
                print("No hay usuarios registrados")
                return

            print(f"\nTotal de usuarios: {len(usuarios)}\n")
            for usuario in usuarios:
                print(f"ID: {usuario.get('id')}")
                print(f"  Nombre: {usuario.get('nombre')} {usuario.get('apellido')}")
                print(f"  Email: {usuario.get('email')}")
                print(f"  Rol: {usuario.get('rol')}")
                print()
        except Exception as e:
            self._mostrar_error(f"Error al listar usuarios: {str(e)}")

    def ver_estudiantes(self):
        """Muestra todos los estudiantes registrados."""
        print("\n--- ESTUDIANTES REGISTRADOS ---")
        try:
            estudiantes = self.fachada.listar_estudiantes()
            if not estudiantes:
                print("No hay estudiantes registrados")
                return

            print(f"\nTotal de estudiantes: {len(estudiantes)}\n")
            for estudiante in estudiantes:
                print(f"ID: {estudiante.get('id')}")
                print(f"  Nombre: {estudiante.get('nombre')} {estudiante.get('apellido')}")
                print(f"  Email: {estudiante.get('email')}")
                print()
        except Exception as e:
            self._mostrar_error(f"Error al listar estudiantes: {str(e)}")

    def ver_docentes(self):
        """Muestra todos los docentes registrados."""
        print("\n--- DOCENTES REGISTRADOS ---")
        try:
            docentes = self.fachada.listar_docentes()
            if not docentes:
                print("No hay docentes registrados")
                return

            print(f"\nTotal de docentes: {len(docentes)}\n")
            for docente in docentes:
                print(f"ID: {docente.get('id')}")
                print(f"  Nombre: {docente.get('nombre')} {docente.get('apellido')}")
                print(f"  Email: {docente.get('email')}")
                print()
        except Exception as e:
            self._mostrar_error(f"Error al listar docentes: {str(e)}")

    def _mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito."""
        print(f"\n✅ {mensaje}")

    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        print(f"\n❌ Error: {mensaje}")

    def ejecutar(self):
        """Ejecuta el ciclo principal de pruebas."""
        print("\n🚀 Iniciando pruebas del sistema UniLevel...\n")

        while True:
            self.mostrar_menu()
            opcion = input("\nSeleccione una opción: ").strip()

            if opcion == "1":
                self.crear_usuario_interactivo()
            elif opcion == "2":
                self.iniciar_sesion_interactivo()
            elif opcion == "3":
                self.matricular_estudiante_interactivo()
            elif opcion == "4":
                self.crear_paralelo_interactivo()
            elif opcion == "5":
                self.crear_tarea_interactivo()
            elif opcion == "6":
                self.registrar_calificacion_interactivo()
            elif opcion == "7":
                self.ver_usuarios()
            elif opcion == "8":
                self.ver_estudiantes()
            elif opcion == "9":
                self.ver_docentes()
            elif opcion == "10":
                print("\n👋 Finalizando pruebas. ¡Hasta pronto!\n")
                break
            else:
                self._mostrar_error("Opción no válida")


if __name__ == "__main__":
    try:
        testador = TestadorSistema()
        testador.ejecutar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario.")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {str(e)}")

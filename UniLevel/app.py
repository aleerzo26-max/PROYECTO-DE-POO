"""
app.py - Punto de entrada de la aplicación Flask UniLevel.

Aquí se inicializa Flask, se configuran las rutas y se orquestan los componentes del sistema.
"""

import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, Response, flash, redirect, render_template, request, session, url_for, send_from_directory

import config
from facades.sistema_nivelacion_facade import SistemaNivelacionFacade
from repositories.usuario_repository import UsuarioRepository
from repositories.matricula_repository import MatriculaRepository
from repositories.paralelo_repository import ParaleloRepository
from repositories.periodo_academico_repository import PeriodoAcademicoRepository
from repositories.notificacion_repository import NotificacionRepository
from repositories.horario_repository import HorarioRepository
from repositories.tarea_repository import TareaRepository
from repositories.entrega_repository import EntregaRepository
from repositories.calificacion_repository import CalificacionRepository
from repositories.asistencia_repository import AsistenciaRepository
from repositories.reporte_repository import ReporteRepository
from services.autenticacion_service import AutenticacionService
from services.usuario_service import UsuarioService
from services.notificacion_service import NotificacionService
from services.matricula_service import MatriculaService
from services.horario_service import HorarioService
from services.paralelo_service import ParaleloService
from services.periodo_academico_service import PeriodoAcademicoService
from services.tarea_service import TareaService
from services.entrega_service import EntregaService
from services.calificacion_service import CalificacionService
from services.asistencia_service import AsistenciaService
from services.reporte_service import ReporteService
from services.importador_service import ImportadorService
from utils.password_generator import PasswordGenerator
from utils.email_sender import EmailSender
from werkzeug.utils import secure_filename
from repositories.carrera_repository import CarreraRepository
from repositories.malla_repository import MallaRepository
from repositories.asignatura_repository import AsignaturaRepository
from repositories.curso_repository import CursoRepository
from services.carrera_service import CarreraService
from services.malla_service import MallaService
from services.asignatura_service import AsignaturaService
from services.curso_service import CursoService


def crear_app(config_name="development"):
    """Factory function para crear la aplicación Flask."""

    app = Flask(__name__)
    config_obj = config.get_config(config_name)
    app.config.from_object(config_obj)

    # Inicializar componentes
    inicializar_componentes(app)

    # Registrar rutas
    registrar_rutas(app)

    return app


def inicializar_componentes(app):
    """Inicializa todos los componentes del sistema en el contexto de la app."""

    # Repositorios
    usuario_repo = UsuarioRepository(app.config["JSON_USUARIOS"])
    matricula_repo = MatriculaRepository(app.config["JSON_MATRICULAS"])
    paralelo_repo = ParaleloRepository(app.config["JSON_PARALELOS"])
    periodo_repo = PeriodoAcademicoRepository(app.config["JSON_PERIODOS"])
    notificacion_repo = NotificacionRepository(app.config["JSON_NOTIFICACIONES"])
    horario_repo = HorarioRepository(app.config["JSON_HORARIOS"])

    # Servicios
    password_gen = PasswordGenerator()
    email_sender = EmailSender()
    notificacion_service = NotificacionService(notificacion_repo)
    horario_service = HorarioService(horario_repo)
    paralelo_service = ParaleloService(paralelo_repo, matricula_repo)
    periodo_service = PeriodoAcademicoService(periodo_repo)

    tarea_repo = TareaRepository(app.config["JSON_TAREAS"])
    entrega_repo = EntregaRepository(app.config["JSON_ENTREGAS"])
    calificacion_repo = CalificacionRepository(app.config["JSON_CALIFICACIONES"])
    asistencia_repo = AsistenciaRepository(app.config["JSON_ASISTENCIAS"])
    reporte_repo = ReporteRepository(app.config["JSON_REPORTES"])

    autenticacion_service = AutenticacionService(usuario_repo)
    usuario_service = UsuarioService(usuario_repo, notificacion_service, password_gen, email_sender)
    matricula_service = MatriculaService(
        matricula_repo,
        paralelo_repo,
        horario_service,
        notificacion_service,
        periodo_service,
    )
    # Conectar el servicio de matrículas al servicio de usuarios para limpieza de referencias
    usuario_service._matricula_service = matricula_service
    tarea_service = TareaService(tarea_repo, paralelo_repo, matricula_repo, notificacion_service)
    entrega_service = EntregaService(entrega_repo, tarea_repo, matricula_repo, notificacion_service)
    calificacion_service = CalificacionService(calificacion_repo, paralelo_repo, matricula_repo, notificacion_service)
    asistencia_service = AsistenciaService(asistencia_repo, paralelo_repo, matricula_repo, notificacion_service)
    reporte_service = ReporteService(
        reporte_repo,
        usuario_repo,
        matricula_repo,
        calificacion_repo,
        asistencia_repo,
        paralelo_repo,
        periodo_repo,
        str(app.config["REPORTES_FOLDER"]),
    )

    # Pasar horario_service a la fachada
    horario_service = HorarioService(horario_repo)

    # Servicio de importación
    importador_service = ImportadorService(
        usuario_repo,
        notificacion_repo,
        None,  # Se pasará la fachada después de crearla
    )

    # Fachada
    fachada = SistemaNivelacionFacade(
        autenticacion_service,
        usuario_service,
        matricula_service,
        paralelo_service,
        periodo_service,
        notificacion_service,
        tarea_service,
        entrega_service,
        calificacion_service,
        asistencia_service,
        horario_service,
        reporte_service,
        importador_service,
    )

    # Registrar servicios del coordinador en la fachada
    # Repos/servicios para coordinador
    carrera_repo = CarreraRepository(app.config["JSON_CARRERAS"]) if "JSON_CARRERAS" in app.config else None
    malla_repo = MallaRepository(app.config["JSON_MALLAS"]) if "JSON_MALLAS" in app.config else None
    asignatura_repo = AsignaturaRepository(app.config["JSON_ASIGNATURAS"]) if "JSON_ASIGNATURAS" in app.config else None
    curso_repo = CursoRepository(app.config["JSON_CURSOS"]) if "JSON_CURSOS" in app.config else None

    if carrera_repo is not None:
        fachada._carrera_service = CarreraService(carrera_repo)
    if malla_repo is not None:
        fachada._malla_service = MallaService(malla_repo)
    if asignatura_repo is not None:
        fachada._asignatura_service = AsignaturaService(asignatura_repo)
    if curso_repo is not None:
        curso_service = CursoService(curso_repo)
        fachada._curso_service = curso_service
        paralelo_service._curso_service = curso_service

    # Actualizar referencia de fachada en el importador
    importador_service._fachada = fachada

    # Exponer fachada y servicios en el contexto de la app
    app.fachada = fachada
    app.usuario_service = usuario_service
    app.matricula_service = matricula_service
    app.paralelo_service = paralelo_service
    app.horario_service = horario_service

    # Almacenar en contexto de la app
    app.fachada = fachada


def registrar_rutas(app):
    """Registra todas las rutas de la aplicación."""

    # ===================== RUTAS PÚBLICAS =====================

    @app.route("/", methods=["GET"])
    def inicio():
        """Ruta raíz - redirige a login o dashboard."""
        if "usuario_id" in session:
            return redirect(url_for(f"dashboard_{session['rol']}"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Ruta de login."""
        if request.method == "POST":
            correo = request.form.get("correo", "").strip()
            password = request.form.get("password", "").strip()

            if not correo or not password:
                flash("Correo y contraseña son requeridos.", "error")
                return redirect(url_for("login"))

            try:
                usuario = app.fachada.iniciar_sesion(correo, password)

                # Almacenar en sesión
                session["usuario_id"] = usuario["id"]
                session["nombre"] = usuario["nombre"]
                session["apellido"] = usuario["apellido"]
                session["rol"] = usuario["rol"]
                session["email"] = usuario["email"]
                session["primer_inicio"] = usuario.get("primer_inicio", False)
                session.permanent = True

                # Verificar si debe cambiar contraseña
                if usuario.get("primer_inicio", False):
                    flash("Debe cambiar su contraseña en el primer inicio.", "warning")
                    return redirect(url_for("cambiar_password"))

                flash(f"Bienvenido {usuario['nombre']}!", "success")
                return redirect(url_for(f"dashboard_{usuario['rol']}"))

            except RuntimeError as e:
                flash(str(e), "error")
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                flash(f"Error inesperado: {str(e)}", "error")

            return redirect(url_for("login"))

        return render_template("auth/login.html")

    @app.route("/logout", methods=["GET"])
    def logout():
        """Ruta de logout."""
        session.clear()
        flash("Sesión cerrada correctamente.", "success")
        return redirect(url_for("login"))

    # ===================== RUTAS PROTEGIDAS =====================

    @app.route("/cambiar-password", methods=["GET", "POST"])
    def cambiar_password():
        """Ruta para cambiar contraseña (primer inicio)."""
        if "usuario_id" not in session:
            flash("Debe iniciar sesión para cambiar su contraseña.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            nueva_password = request.form.get("nueva_password", "").strip()
            confirmar_password = request.form.get("confirmar_password", "").strip()

            if not nueva_password or not confirmar_password:
                flash("Todos los campos son requeridos.", "error")
                return redirect(url_for("cambiar_password"))

            if nueva_password != confirmar_password:
                flash("Las contraseñas no coinciden.", "error")
                return redirect(url_for("cambiar_password"))

            if len(nueva_password) < 6:
                flash("La contraseña debe tener al menos 6 caracteres.", "error")
                return redirect(url_for("cambiar_password"))

            try:
                app.fachada.cambiar_password(session["usuario_id"], nueva_password)
                session["primer_inicio"] = False
                session["password_temporal"] = False
                try:
                    # Eliminar credenciales temporales almacenadas en notificaciones
                    app.fachada.eliminar_notificaciones_credenciales_por_usuario(session.get("usuario_id"))
                except Exception:
                    pass
                flash("Contraseña actualizada correctamente.", "success")
                return redirect(url_for(f"dashboard_{session['rol']}"))
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                flash(f"Error inesperado: {str(e)}", "error")

            return redirect(url_for("cambiar_password"))

        return render_template(
            "auth/cambiar_password.html",
            usuario_nombre=session.get("nombre", ""),
            usuario_apellido=session.get("apellido", ""),
            usuario_email=session.get("email", ""),
            usuario_rol=session.get("rol", ""),
        )

    # ===================== DASHBOARDS =====================

    @app.route("/dashboard/admin", methods=["GET"])
    def dashboard_administrador():
        """Dashboard para administrador."""
        if not _validar_sesion(session, "administrador"):
            return redirect(url_for("login"))

        usuarios = app.fachada.listar_usuarios()
        context = {
            "usuario": {
                "nombre": session.get("nombre"),
                "apellido": session.get("apellido"),
                "email": session.get("email"),
                "rol": session.get("rol"),
            },
            "total_usuarios": len(usuarios),
            "total_estudiantes": len(app.fachada.listar_estudiantes()),
            "total_docentes": len(app.fachada.listar_docentes()),
            "total_paralelos": len(app.fachada.listar_paralelos()),
        }
        return render_template("admin/dashboard_admin.html", **context)

    @app.route("/dashboard/docente", methods=["GET"])
    def dashboard_docente():
        """Dashboard para docente."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        paralelos_docente = app.fachada.listar_paralelos_por_docente(session["usuario_id"])
        paralelo_ids = {paralelo.get("id") for paralelo in paralelos_docente}
        estudiantes = app.fachada.listar_estudiantes_por_docente(session["usuario_id"])
        estudiantes_docente = {e.get("id") for e in estudiantes}

        tareas_docente = app.fachada.listar_tareas_docente(session["usuario_id"])
        calificaciones_docente = app.fachada.listar_calificaciones_docente(session["usuario_id"])
        tareas_recientes = []
        for tarea in tareas_docente[:3]:
            paralelo = app.fachada.obtener_paralelo_por_id(tarea.get("paralelo_id"))
            entregas = app.fachada.listar_entregas_tarea(tarea.get("id"))
            tareas_recientes.append({
                **tarea,
                "paralelo_nombre": paralelo.get("nombre", "N/D") if paralelo else "N/D",
                "entregas_count": len(entregas),
            })

        context = {
            "usuario": {
                "nombre": session.get("nombre"),
                "apellido": session.get("apellido"),
                "email": session.get("email"),
                "rol": session.get("rol"),
            },
            "mis_cursos": len(paralelos_docente),
            "paralelos": paralelos_docente,
            "estudiantes": estudiantes,
            "total_estudiantes": len(estudiantes_docente),
            "tareas_pendientes": len(tareas_docente),
            "calificaciones": len(calificaciones_docente),
            "tareas_recientes": tareas_recientes,
        }
        return render_template("docente/dashboard_docente.html", **context)

    @app.route("/dashboard/estudiante", methods=["GET"])
    def dashboard_estudiante():
        """Dashboard para estudiante."""
        if not _validar_sesion(session, "estudiante"):
            return redirect(url_for("login"))

        matricula_activa = app.fachada.obtener_matricula_activa_por_estudiante(session["usuario_id"])
        tareas_estudiante = app.fachada.listar_tareas_estudiante(session["usuario_id"])
        entregas_estudiante = app.fachada.listar_entregas_estudiante(session["usuario_id"])
        tareas_recientes = []
        for tarea in tareas_estudiante[:3]:
            paralelo = app.fachada.obtener_paralelo_por_id(tarea.get("paralelo_id"))
            entrega = app.fachada.obtener_entrega_por_tarea_y_estudiante(tarea.get("id"), session["usuario_id"])
            tareas_recientes.append({
                **tarea,
                "paralelo_nombre": paralelo.get("nombre", "N/D") if paralelo else "N/D",
                "estado_tarea": "Entregado" if entrega else "Pendiente",
            })
        # Información de matrícula/paralelo/horario para el estudiante
        if matricula_activa is None:
            paralelo_info = None
            docente_info = None
            horario_info = None
            mensaje_matricula = "No posee una matrícula activa."
        else:
            paralelo_info = app.fachada.obtener_paralelo_por_id(matricula_activa.get("paralelo_id"))
            docente_info = None
            if paralelo_info and paralelo_info.get("docente_id"):
                docente_info = app.fachada.obtener_usuario_por_id(paralelo_info.get("docente_id"))
            horario_info = app.fachada.obtener_horario_por_matricula(matricula_activa.get("id"))
            mensaje_matricula = None

        context = {
            "usuario": {
                "nombre": session.get("nombre"),
                "apellido": session.get("apellido"),
                "email": session.get("email"),
                "rol": session.get("rol"),
            },
            "mis_cursos": 1 if matricula_activa else 0,
            "matricula_activa": matricula_activa,
            "paralelo": paralelo_info,
            "docente_paralelo": docente_info,
            "horario": horario_info,
            "mensaje_matricula": mensaje_matricula,
            "tareas_pendientes": len(tareas_estudiante),
            "tareas_completadas": len(entregas_estudiante),
            "promedio_academico": app.fachada.calcular_promedio_estudiante(session["usuario_id"]),
            "notificaciones_no_leidas": app.fachada.contar_notificaciones_no_leidas(session["usuario_id"]),
            "notificaciones_recientes": app.fachada.listar_notificaciones_recientes(session["usuario_id"]),
            "tareas_recientes": tareas_recientes,
        }
        return render_template("estudiante/dashboard_estudiante.html", **context)

    @app.route("/notificaciones", methods=["GET"])
    def listar_notificaciones():
        """Lista todas las notificaciones del usuario autenticado."""
        if not _validar_sesion(session):
            return redirect(url_for("login"))

        try:
            notificaciones = app.fachada.listar_notificaciones(session["usuario_id"])
            return render_template(
                "notificaciones.html",
                notificaciones=notificaciones,
                active_page="notificaciones",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("dashboard_estudiante"))

    @app.route("/notificaciones/<notificacion_id>/leer", methods=["POST"])
    def marcar_notificacion_leida(notificacion_id):
        """Marca una notificación como leída."""
        if not _validar_sesion(session):
            return redirect(url_for("login"))

        try:
            app.fachada.marcar_notificacion_como_leida(notificacion_id, session["usuario_id"])
            flash("Notificación marcada como leída.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("listar_notificaciones"))

    @app.route("/notificaciones/marcar_todas", methods=["POST"])
    def marcar_todas_notificaciones_leidas():
        """Marca todas las notificaciones del usuario como leídas."""
        if not _validar_sesion(session):
            return redirect(url_for("login"))

        try:
            total = app.fachada.marcar_todas_notificaciones_como_leidas(session["usuario_id"])
            flash(f"{total} notificación(es) marcadas como leídas.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("listar_notificaciones"))

    @app.route("/notificaciones/<notificacion_id>/eliminar", methods=["POST"])
    def eliminar_notificacion(notificacion_id):
        """Elimina una notificación del usuario."""
        if not _validar_sesion(session):
            return redirect(url_for("login"))

        try:
            app.fachada.eliminar_notificacion(notificacion_id, session["usuario_id"])
            flash("Notificación eliminada correctamente.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("listar_notificaciones"))

    @app.route("/dashboard/coordinador", methods=["GET"])
    def dashboard_coordinador():
        """Dashboard para coordinador."""
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))

        cursos_activos = app.fachada.listar_paralelos()
        context = {
            "usuario": {
                "nombre": session.get("nombre"),
                "apellido": session.get("apellido"),
                "email": session.get("email"),
                "rol": session.get("rol"),
            },
            "total_estudiantes": len(app.fachada.listar_estudiantes()),
            "total_cursos": len(cursos_activos),
            "total_docentes": len(app.fachada.listar_docentes()),
            "tasa_aprobacion": app.fachada.calcular_tasa_aprobacion(),
            "cursos_activos": cursos_activos,
        }
        return render_template("coordinador/dashboard_coordinador.html", **context)

    # ===================== GESTIÓN DE TAREAS DOCENTE =====================

    @app.route("/docente/tareas", methods=["GET"])
    def listar_tareas_docente():
        """Lista las tareas creadas por el docente."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            tareas = app.fachada.listar_tareas_docente(session["usuario_id"])
            tareas_detalle = []
            for tarea in tareas:
                paralelo = app.fachada.obtener_paralelo_por_id(tarea.get("paralelo_id"))
                entregas = app.fachada.listar_entregas_tarea(tarea.get("id"))
                tareas_detalle.append({**tarea, "paralelo": paralelo, "entregas": entregas})

            return render_template(
                "docente/tareas/listar.html",
                tareas=tareas_detalle,
                active_page="tareas_docente",
            )
        except Exception as e:
            flash(f"Error al listar tareas: {str(e)}", "error")
            return redirect(url_for("dashboard_docente"))

    @app.route("/docente/tareas/crear", methods=["GET", "POST"])
    def crear_tarea_docente():
        """Crear una tarea para un paralelo asignado."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        if request.method == "POST":
            try:
                titulo = request.form.get("titulo", "").strip()
                descripcion = request.form.get("descripcion", "").strip()
                paralelo_id = request.form.get("paralelo_id", "").strip()
                fecha_entrega = request.form.get("fecha_entrega", "").strip()
                archivo = request.files.get("archivo")

                if archivo and archivo.filename:
                    archivo_guardado = _guardar_archivo_subido(archivo)
                else:
                    archivo_guardado = ""

                datos = {
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "paralelo_id": paralelo_id,
                    "fecha_entrega": fecha_entrega,
                    "archivo_instrucciones": archivo_guardado,
                }

                app.fachada.crear_tarea(datos, session["usuario_id"])
                flash("Tarea creada correctamente.", "success")
                return redirect(url_for("listar_tareas_docente"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("crear_tarea_docente"))

        paralelos = [
            paralelo
            for paralelo in app.fachada.listar_paralelos()
            if paralelo.get("docente_id") == session["usuario_id"]
        ]

        return render_template(
            "docente/tareas/crear.html",
            paralelos=paralelos,
            active_page="tareas_docente",
        )

    @app.route("/docente/tareas/<tarea_id>", methods=["GET"])
    def ver_tarea_docente(tarea_id):
        """Ver los detalles de una tarea y sus entregas."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            tarea = app.fachada.obtener_tarea(tarea_id)
            if tarea.get("docente_id") != session["usuario_id"]:
                flash("Acceso denegado.", "error")
                return redirect(url_for("listar_tareas_docente"))

            paralelo = app.fachada.obtener_paralelo_por_id(tarea.get("paralelo_id"))
            entregas = app.fachada.listar_entregas_tarea(tarea_id)
            entregas_detalle = []
            for entrega in entregas:
                estudiante = app.fachada.obtener_usuario_por_id(entrega.get("estudiante_id"))
                entregas_detalle.append({**entrega, "estudiante": estudiante})

            return render_template(
                "docente/tareas/ver.html",
                tarea=tarea,
                paralelo=paralelo,
                entregas=entregas_detalle,
                active_page="tareas_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_tareas_docente"))

    @app.route("/docente/entregas/<entrega_id>/calificar", methods=["GET", "POST"])
    def calificar_entrega_docente(entrega_id):
        """Calificar una entrega realizada por un estudiante."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            entrega = app.fachada.obtener_entrega(entrega_id)
            tarea = app.fachada.obtener_tarea(entrega.get("tarea_id"))

            if tarea.get("docente_id") != session["usuario_id"]:
                flash("Acceso denegado.", "error")
                return redirect(url_for("listar_tareas_docente"))

            if request.method == "POST":
                puntuacion = float(request.form.get("puntuacion", "0"))
                comentario = request.form.get("comentario", "").strip()
                app.fachada.calificar_entrega(entrega_id, session["usuario_id"], puntuacion, comentario)
                flash("Entrega calificada correctamente.", "success")
                return redirect(url_for("ver_tarea_docente", tarea_id=tarea.get("id")))

            estudiante = app.fachada.obtener_usuario_por_id(entrega.get("estudiante_id"))
            return render_template(
                "docente/entregas/calificar.html",
                entrega=entrega,
                tarea=tarea,
                estudiante=estudiante,
                active_page="tareas_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_tareas_docente"))

    # ===================== GESTIÓN DE CALIFICACIONES DOCENTE =====================

    @app.route("/docente/calificaciones", methods=["GET"])
    def listar_calificaciones_docente():
        """Lista las calificaciones registradas por el docente."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            calificaciones = app.fachada.listar_calificaciones_docente(session["usuario_id"])
            calificaciones_detalle = []
            for calificacion in calificaciones:
                estudiante = app.fachada.obtener_usuario_por_id(calificacion.get("estudiante_id"))
                paralelo = app.fachada.obtener_paralelo_por_id(calificacion.get("paralelo_id"))
                calificaciones_detalle.append(
                    {
                        **calificacion,
                        "estudiante_nombre": f"{estudiante.get('nombre', '')} {estudiante.get('apellido', '')}" if estudiante else "Estudiante desconocido",
                        "paralelo_nombre": paralelo.get("nombre") if paralelo else "Paralelo no encontrado",
                    }
                )

            return render_template(
                "docente/calificaciones/listar.html",
                calificaciones=calificaciones_detalle,
                active_page="calificaciones_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("dashboard_docente"))

    @app.route("/docente/calificaciones/registrar", methods=["GET", "POST"])
    def registrar_calificacion_docente():
        """Registra una nueva calificación para un estudiante matriculado."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            if request.method == "POST":
                datos = {
                    "estudiante_id": request.form.get("estudiante_id", ""),
                    "paralelo_id": request.form.get("paralelo_id", ""),
                    "evaluacion": request.form.get("evaluacion", "").strip(),
                    "nota": request.form.get("nota", ""),
                    "comentario": request.form.get("comentario", "").strip(),
                }
                app.fachada.registrar_calificacion(datos, session["usuario_id"])
                flash("Calificación registrada correctamente.", "success")
                return redirect(url_for("listar_calificaciones_docente"))

            paralelos = [
                paralelo
                for paralelo in app.fachada.listar_paralelos()
                if paralelo.get("docente_id") == session["usuario_id"]
            ]

            estudiantes = []
            for paralelo in paralelos:
                matriculas = app.fachada.listar_matriculas()
                for matricula in matriculas:
                    if (
                        isinstance(matricula, dict)
                        and matricula.get("paralelo_id") == paralelo.get("id")
                        and str(matricula.get("estado", "")).lower() == "matriculado"
                    ):
                        estudiante = app.fachada.obtener_usuario_por_id(matricula.get("estudiante_id"))
                        if estudiante:
                            estudiantes.append(
                                {
                                    "id": estudiante.get("id"),
                                    "nombre": estudiante.get("nombre", ""),
                                    "apellido": estudiante.get("apellido", ""),
                                    "paralelo_nombre": paralelo.get("nombre"),
                                }
                            )

            return render_template(
                "docente/calificaciones/registrar.html",
                paralelos=paralelos,
                estudiantes=estudiantes,
                active_page="calificaciones_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_calificaciones_docente"))

    @app.route("/docente/calificaciones/<calificacion_id>/editar", methods=["GET", "POST"])
    def editar_calificacion_docente(calificacion_id):
        """Edita una calificación previamente registrada."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            calificacion = app.fachada.obtener_calificacion(calificacion_id)
            paralelo = app.fachada.obtener_paralelo_por_id(calificacion.get("paralelo_id"))
            if paralelo.get("docente_id") != session["usuario_id"]:
                flash("Acceso denegado.", "error")
                return redirect(url_for("listar_calificaciones_docente"))

            if request.method == "POST":
                datos = {
                    "evaluacion": request.form.get("evaluacion", "").strip(),
                    "nota": request.form.get("nota", ""),
                    "comentario": request.form.get("comentario", "").strip(),
                }
                app.fachada.editar_calificacion(calificacion_id, datos, session["usuario_id"])
                flash("Calificación actualizada correctamente.", "success")
                return redirect(url_for("detalle_calificacion_docente", calificacion_id=calificacion_id))

            return render_template(
                "docente/calificaciones/editar.html",
                calificacion=calificacion,
                active_page="calificaciones_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_calificaciones_docente"))

    @app.route("/docente/calificaciones/<calificacion_id>", methods=["GET"])
    def detalle_calificacion_docente(calificacion_id):
        """Muestra el detalle de una calificación registrada."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            calificacion = app.fachada.obtener_calificacion(calificacion_id)
            paralelo = app.fachada.obtener_paralelo_por_id(calificacion.get("paralelo_id"))
            if paralelo.get("docente_id") != session["usuario_id"]:
                flash("Acceso denegado.", "error")
                return redirect(url_for("listar_calificaciones_docente"))

            estudiante = app.fachada.obtener_usuario_por_id(calificacion.get("estudiante_id"))
            calificacion_detalle = {
                **calificacion,
                "estudiante_nombre": f"{estudiante.get('nombre', '')} {estudiante.get('apellido', '')}" if estudiante else "Estudiante desconocido",
                "paralelo_nombre": paralelo.get("nombre") if paralelo else "Paralelo no encontrado",
            }

            return render_template(
                "docente/calificaciones/detalle.html",
                calificacion=calificacion_detalle,
                active_page="calificaciones_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_calificaciones_docente"))

    # ===================== GESTIÓN DE ASISTENCIAS DOCENTE =====================

    @app.route("/docente/asistencias", methods=["GET"])
    def listar_asistencias_docente():
        """Lista los registros de asistencia del docente."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            paralelo_id = request.args.get("paralelo_id", "").strip()
            fecha = request.args.get("fecha", "").strip()
            filtros = {}
            if paralelo_id:
                filtros["paralelo_id"] = paralelo_id
            if fecha:
                filtros["fecha"] = fecha

            asistencias = app.fachada.listar_asistencias_docente(session["usuario_id"], filtros)
            asistencias_detalle = []
            for asistencia in asistencias:
                estudiante = app.fachada.obtener_usuario_por_id(asistencia.get("estudiante_id"))
                paralelo = app.fachada.obtener_paralelo_por_id(asistencia.get("paralelo_id"))
                asistencias_detalle.append(
                    {
                        **asistencia,
                        "estudiante_nombre": f"{estudiante.get('nombre', '')} {estudiante.get('apellido', '')}" if estudiante else "Estudiante desconocido",
                        "paralelo_nombre": paralelo.get("nombre") if paralelo else "Paralelo no encontrado",
                    }
                )

            paralelos = [
                paralelo
                for paralelo in app.fachada.listar_paralelos()
                if paralelo.get("docente_id") == session["usuario_id"]
            ]

            return render_template(
                "docente/asistencias.html",
                asistencias=asistencias_detalle,
                paralelos=paralelos,
                filtro_paralelo=paralelo_id,
                filtro_fecha=fecha,
                active_page="asistencias_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("dashboard_docente"))

    @app.route("/docente/asistencias/registrar", methods=["GET", "POST"])
    def registrar_asistencia_docente():
        """Registra una nueva asistencia para un estudiante."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            if request.method == "POST":
                datos = {
                    "estudiante_id": request.form.get("estudiante_id", ""),
                    "paralelo_id": request.form.get("paralelo_id", ""),
                    "fecha": request.form.get("fecha", ""),
                    "asistio": request.form.get("asistio", ""),
                    "comentario": request.form.get("comentario", "").strip(),
                }
                app.fachada.registrar_asistencia(datos, session["usuario_id"])
                flash("Asistencia registrada correctamente.", "success")
                return redirect(url_for("listar_asistencias_docente"))

            paralelos = [
                paralelo
                for paralelo in app.fachada.listar_paralelos()
                if paralelo.get("docente_id") == session["usuario_id"]
            ]

            estudiantes = []
            estudiantes_ids = set()
            matriculas = app.fachada.listar_matriculas()
            for paralelo in paralelos:
                for matricula in matriculas:
                    if (
                        isinstance(matricula, dict)
                        and matricula.get("paralelo_id") == paralelo.get("id")
                        and str(matricula.get("estado", "")).lower() == "matriculado"
                    ):
                        estudiante_id = matricula.get("estudiante_id")
                        if estudiante_id and estudiante_id not in estudiantes_ids:
                            estudiante = app.fachada.obtener_usuario_por_id(estudiante_id)
                            if estudiante:
                                estudiantes_ids.add(estudiante_id)
                                estudiantes.append(
                                    {
                                        "id": estudiante_id,
                                        "nombre": f"{estudiante.get('nombre', '')} {estudiante.get('apellido', '')}",
                                        "paralelo_nombre": paralelo.get("nombre"),
                                    }
                                )

            return render_template(
                "docente/asistencias/registrar.html",
                paralelos=paralelos,
                estudiantes=estudiantes,
                active_page="asistencias_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_asistencias_docente"))

    @app.route("/docente/asistencias/<asistencia_id>/editar", methods=["GET", "POST"])
    def editar_asistencia_docente(asistencia_id):
        """Edita un registro de asistencia existente."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            asistencia = app.fachada.obtener_asistencia(asistencia_id)
            paralelo = app.fachada.obtener_paralelo_por_id(asistencia.get("paralelo_id"))
            if paralelo.get("docente_id") != session["usuario_id"]:
                flash("Acceso denegado.", "error")
                return redirect(url_for("listar_asistencias_docente"))

            if request.method == "POST":
                datos = {
                    "fecha": request.form.get("fecha", ""),
                    "asistio": request.form.get("asistio", ""),
                    "comentario": request.form.get("comentario", "").strip(),
                }
                app.fachada.editar_asistencia(asistencia_id, datos, session["usuario_id"])
                flash("Asistencia actualizada correctamente.", "success")
                return redirect(url_for("detalle_asistencia_docente", asistencia_id=asistencia_id))

            estudiante = app.fachada.obtener_usuario_por_id(asistencia.get("estudiante_id"))
            asistencia_detalle = {
                **asistencia,
                "estudiante_nombre": f"{estudiante.get('nombre', '')} {estudiante.get('apellido', '')}" if estudiante else "Estudiante desconocido",
                "paralelo_nombre": paralelo.get("nombre") if paralelo else "Paralelo no encontrado",
            }

            return render_template(
                "docente/asistencias/editar.html",
                asistencia=asistencia_detalle,
                active_page="asistencias_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_asistencias_docente"))

    @app.route("/docente/asistencias/<asistencia_id>", methods=["GET"])
    def detalle_asistencia_docente(asistencia_id):
        """Muestra el detalle de una asistencia registrada."""
        if not _validar_sesion(session, "docente"):
            return redirect(url_for("login"))

        try:
            asistencia = app.fachada.obtener_asistencia(asistencia_id)
            paralelo = app.fachada.obtener_paralelo_por_id(asistencia.get("paralelo_id"))
            if paralelo.get("docente_id") != session["usuario_id"]:
                flash("Acceso denegado.", "error")
                return redirect(url_for("listar_asistencias_docente"))

            estudiante = app.fachada.obtener_usuario_por_id(asistencia.get("estudiante_id"))
            asistencia_detalle = {
                **asistencia,
                "estudiante_nombre": f"{estudiante.get('nombre', '')} {estudiante.get('apellido', '')}" if estudiante else "Estudiante desconocido",
                "paralelo_nombre": paralelo.get("nombre") if paralelo else "Paralelo no encontrado",
            }

            return render_template(
                "docente/asistencias/detalle.html",
                asistencia=asistencia_detalle,
                active_page="asistencias_docente",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_asistencias_docente"))

    # ===================== GESTIÓN DE TAREAS ESTUDIANTE =====================

    @app.route("/estudiante/calificaciones", methods=["GET"])
    def mis_calificaciones_estudiante():
        """Lista las calificaciones del estudiante y muestra el promedio."""
        if not _validar_sesion(session, "estudiante"):
            return redirect(url_for("login"))

        try:
            calificaciones = app.fachada.listar_calificaciones_estudiante(session["usuario_id"])
            calificaciones_detalle = []
            for calificacion in calificaciones:
                paralelo = app.fachada.obtener_paralelo_por_id(calificacion.get("paralelo_id"))
                calificaciones_detalle.append(
                    {
                        **calificacion,
                        "paralelo_nombre": paralelo.get("nombre") if paralelo else "Paralelo no encontrado",
                    }
                )

            promedio = app.fachada.calcular_promedio_estudiante(session["usuario_id"])
            return render_template(
                "estudiante/calificaciones/mis_calificaciones.html",
                calificaciones=calificaciones_detalle,
                promedio=promedio,
                active_page="mis_calificaciones",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("dashboard_estudiante"))

    # ===================== RUTAS COORDINADOR =====================

    @app.route("/coordinador/carreras", methods=["GET"])
    def listar_carreras():
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        carreras = app.fachada.listar_carreras()
        return render_template("coordinador/carreras_listar.html", carreras=carreras, active_page="carreras")

    @app.route("/coordinador/carreras/crear", methods=["GET", "POST"])
    def crear_carrera():
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        if request.method == "POST":
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "codigo": request.form.get("codigo", "").strip(),
                "descripcion": request.form.get("descripcion", "").strip(),
            }
            try:
                app.fachada.crear_carrera(datos)
                flash("Carrera creada correctamente.", "success")
                return redirect(url_for("listar_carreras"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("crear_carrera"))
        return render_template("coordinador/carreras_form.html", carrera=None)

    @app.route("/coordinador/carreras/<carrera_id>/editar", methods=["GET", "POST"])
    def editar_carrera(carrera_id):
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        carrera = app.fachada.obtener_carrera(carrera_id)
        if carrera is None:
            flash("Carrera no encontrada.", "error")
            return redirect(url_for("listar_carreras"))
        if request.method == "POST":
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "codigo": request.form.get("codigo", "").strip(),
                "descripcion": request.form.get("descripcion", "").strip(),
            }
            try:
                app.fachada.editar_carrera(carrera_id, datos)
                flash("Carrera actualizada.", "success")
                return redirect(url_for("listar_carreras"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("editar_carrera", carrera_id=carrera_id))
        return render_template("coordinador/carreras_form.html", carrera=carrera)

    @app.route("/coordinador/carreras/<carrera_id>/eliminar", methods=["POST"])
    def eliminar_carrera(carrera_id):
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        try:
            app.fachada.eliminar_carrera(carrera_id)
            flash("Carrera eliminada.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("listar_carreras"))

    # Mallas
    @app.route("/coordinador/mallas", methods=["GET"])
    def listar_mallas():
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        mallas = app.fachada.listar_mallas()
        return render_template("coordinador/mallas_listar.html", mallas=mallas, active_page="mallas")

    @app.route("/coordinador/mallas/crear", methods=["GET", "POST"])
    def crear_malla():
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        if request.method == "POST":
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "carrera_id": request.form.get("carrera_id"),
                "descripcion": request.form.get("descripcion", "").strip(),
            }
            try:
                app.fachada.crear_malla(datos)
                flash("Malla creada correctamente.", "success")
                return redirect(url_for("listar_mallas"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("crear_malla"))
        carreras = app.fachada.listar_carreras()
        return render_template("coordinador/mallas_form.html", malla=None, carreras=carreras)

    @app.route("/coordinador/mallas/<malla_id>/editar", methods=["GET", "POST"])
    def editar_malla(malla_id):
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        malla = app.fachada.obtener_malla(malla_id)
        if malla is None:
            flash("Malla no encontrada.", "error")
            return redirect(url_for("listar_mallas"))
        if request.method == "POST":
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "carrera_id": request.form.get("carrera_id"),
                "descripcion": request.form.get("descripcion", "").strip(),
            }
            try:
                app.fachada.editar_malla(malla_id, datos)
                flash("Malla actualizada.", "success")
                return redirect(url_for("listar_mallas"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("editar_malla", malla_id=malla_id))
        carreras = app.fachada.listar_carreras()
        return render_template("coordinador/mallas_form.html", malla=malla, carreras=carreras)

    @app.route("/coordinador/mallas/<malla_id>/eliminar", methods=["POST"])
    def eliminar_malla(malla_id):
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        try:
            app.fachada.eliminar_malla(malla_id)
            flash("Malla eliminada.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("listar_mallas"))

    # Asignaturas
    @app.route("/coordinador/asignaturas", methods=["GET"])
    def listar_asignaturas():
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        asignaturas = app.fachada.listar_asignaturas()
        return render_template("coordinador/asignaturas_listar.html", asignaturas=asignaturas, active_page="asignaturas")

    @app.route("/coordinador/asignaturas/crear", methods=["GET", "POST"])
    def crear_asignatura():
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        if request.method == "POST":
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "codigo": request.form.get("codigo", "").strip(),
                "creditos": int(request.form.get("creditos", 0)),
                "descripcion": request.form.get("descripcion", "").strip(),
            }
            try:
                app.fachada.crear_asignatura(datos)
                flash("Asignatura creada correctamente.", "success")
                return redirect(url_for("listar_asignaturas"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("crear_asignatura"))
        return render_template("coordinador/asignaturas_form.html", asignatura=None)

    @app.route("/coordinador/asignaturas/<asignatura_id>/editar", methods=["GET", "POST"])
    def editar_asignatura(asignatura_id):
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        asignatura = app.fachada.obtener_asignatura(asignatura_id)
        if asignatura is None:
            flash("Asignatura no encontrada.", "error")
            return redirect(url_for("listar_asignaturas"))
        if request.method == "POST":
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "codigo": request.form.get("codigo", "").strip(),
                "creditos": int(request.form.get("creditos", 0)),
                "descripcion": request.form.get("descripcion", "").strip(),
            }
            try:
                app.fachada.editar_asignatura(asignatura_id, datos)
                flash("Asignatura actualizada.", "success")
                return redirect(url_for("listar_asignaturas"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("editar_asignatura", asignatura_id=asignatura_id))
        return render_template("coordinador/asignaturas_form.html", asignatura=asignatura)

    @app.route("/coordinador/asignaturas/<asignatura_id>/eliminar", methods=["POST"])
    def eliminar_asignatura(asignatura_id):
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        try:
            app.fachada.eliminar_asignatura(asignatura_id)
            flash("Asignatura eliminada.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("listar_asignaturas"))

    # Cursos
    @app.route("/coordinador/cursos", methods=["GET"])
    def listar_cursos():
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        cursos = app.fachada.listar_cursos()
        return render_template("coordinador/cursos_listar.html", cursos=cursos, active_page="cursos")

    @app.route("/coordinador/cursos/crear", methods=["GET", "POST"])
    def crear_curso():
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        if request.method == "POST":
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "asignatura_id": request.form.get("asignatura_id"),
                "malla_id": request.form.get("malla_id"),
                "descripcion": request.form.get("descripcion", "").strip(),
            }
            try:
                app.fachada.crear_curso(datos)
                flash("Curso creado correctamente.", "success")
                return redirect(url_for("listar_cursos"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("crear_curso"))
        asignaturas = app.fachada.listar_asignaturas()
        mallas = app.fachada.listar_mallas()
        return render_template("coordinador/cursos_form.html", curso=None, asignaturas=asignaturas, mallas=mallas)

    @app.route("/coordinador/cursos/<curso_id>/editar", methods=["GET", "POST"])
    def editar_curso(curso_id):
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        curso = app.fachada.obtener_curso(curso_id)
        if curso is None:
            flash("Curso no encontrado.", "error")
            return redirect(url_for("listar_cursos"))
        if request.method == "POST":
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "asignatura_id": request.form.get("asignatura_id"),
                "malla_id": request.form.get("malla_id"),
                "descripcion": request.form.get("descripcion", "").strip(),
            }
            try:
                app.fachada.editar_curso(curso_id, datos)
                flash("Curso actualizado.", "success")
                return redirect(url_for("listar_cursos"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("editar_curso", curso_id=curso_id))
        asignaturas = app.fachada.listar_asignaturas()
        mallas = app.fachada.listar_mallas()
        return render_template("coordinador/cursos_form.html", curso=curso, asignaturas=asignaturas, mallas=mallas)

    @app.route("/coordinador/cursos/<curso_id>/eliminar", methods=["POST"])
    def eliminar_curso(curso_id):
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        try:
            app.fachada.eliminar_curso(curso_id)
            flash("Curso eliminado.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("listar_cursos"))

    # Paralelos para coordinador (listar y asignar docente)
    @app.route("/coordinador/paralelos", methods=["GET"])
    def listar_paralelos_coordinador():
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))
        paralelos = app.fachada.listar_paralelos()
        return render_template("coordinador/paralelos_listar.html", paralelos=paralelos, active_page="paralelos")

    @app.route("/coordinador/paralelos/<paralelo_id>/asignar", methods=["GET", "POST"])
    def asignar_docente_paralelo_coordinador(paralelo_id):
        if not _validar_sesion(session, "coordinador"):
            return redirect(url_for("login"))

        paralelo = app.fachada.obtener_paralelo_por_id(paralelo_id)
        if paralelo is None:
            flash("Paralelo no encontrado.", "error")
            return redirect(url_for("listar_paralelos_coordinador"))

        if request.method == "POST":
            docente_id = request.form.get("docente_id") or None
            try:
                app.fachada.asignar_docente_paralelo(paralelo_id, docente_id)
                flash("Docente asignado correctamente.", "success")
                return redirect(url_for("listar_paralelos_coordinador"))
            except Exception as e:
                flash(str(e), "error")
                return redirect(url_for("asignar_docente_paralelo_coordinador", paralelo_id=paralelo_id))

        docentes = app.fachada.listar_docentes()
        return render_template("coordinador/paralelos_asignar.html", paralelo=paralelo, docentes=docentes)

    @app.route("/estudiante/calificaciones/<calificacion_id>", methods=["GET"])
    def detalle_calificacion_estudiante(calificacion_id):
        """Muestra el detalle de una calificación para el estudiante."""
        if not _validar_sesion(session, "estudiante"):
            return redirect(url_for("login"))

        try:
            calificacion = app.fachada.obtener_calificacion(calificacion_id)
            if calificacion.get("estudiante_id") != session["usuario_id"]:
                flash("Acceso denegado.", "error")
                return redirect(url_for("mis_calificaciones_estudiante"))

            paralelo = app.fachada.obtener_paralelo_por_id(calificacion.get("paralelo_id"))
            calificacion_detalle = {
                **calificacion,
                "paralelo_nombre": paralelo.get("nombre") if paralelo else "Paralelo no encontrado",
            }

            return render_template(
                "estudiante/calificaciones/detalle.html",
                calificacion=calificacion_detalle,
                active_page="mis_calificaciones",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("mis_calificaciones_estudiante"))

    @app.route("/estudiante/asistencias", methods=["GET"])
    def mis_asistencias_estudiante():
        """Lista el historial de asistencias y el porcentaje para el estudiante."""
        if not _validar_sesion(session, "estudiante"):
            return redirect(url_for("login"))

        try:
            asistencias = app.fachada.listar_asistencias_estudiante(session["usuario_id"])
            asistencias_detalle = []
            for asistencia in asistencias:
                paralelo = app.fachada.obtener_paralelo_por_id(asistencia.get("paralelo_id"))
                asistencias_detalle.append(
                    {
                        **asistencia,
                        "paralelo_nombre": paralelo.get("nombre") if paralelo else "Paralelo no encontrado",
                    }
                )

            porcentaje = app.fachada.calcular_porcentaje_asistencia_estudiante(session["usuario_id"])
            return render_template(
                "estudiante/mis_asistencias.html",
                asistencias=asistencias_detalle,
                porcentaje=porcentaje,
                active_page="mis_asistencias",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("dashboard_estudiante"))

    @app.route("/estudiante/asistencias/<asistencia_id>", methods=["GET"])
    def detalle_asistencia_estudiante(asistencia_id):
        """Muestra el detalle de una asistencia para el estudiante."""
        if not _validar_sesion(session, "estudiante"):
            return redirect(url_for("login"))

        try:
            asistencia = app.fachada.obtener_asistencia(asistencia_id)
            if asistencia.get("estudiante_id") != session["usuario_id"]:
                flash("Acceso denegado.", "error")
                return redirect(url_for("mis_asistencias_estudiante"))

            paralelo = app.fachada.obtener_paralelo_por_id(asistencia.get("paralelo_id"))
            asistencia_detalle = {
                **asistencia,
                "paralelo_nombre": paralelo.get("nombre") if paralelo else "Paralelo no encontrado",
            }

            return render_template(
                "estudiante/detalle_asistencia.html",
                asistencia=asistencia_detalle,
                active_page="mis_asistencias",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("mis_asistencias_estudiante"))

    @app.route("/estudiante/tareas", methods=["GET"])
    def listar_tareas_estudiante():
        """Lista las tareas disponibles para el estudiante."""
        if not _validar_sesion(session, "estudiante"):
            return redirect(url_for("login"))

        try:
            tareas = app.fachada.listar_tareas_estudiante(session["usuario_id"])
            tareas_detalle = []
            for tarea in tareas:
                paralelo = app.fachada.obtener_paralelo_por_id(tarea.get("paralelo_id"))
                entrega = app.fachada.obtener_entrega_por_tarea_y_estudiante(tarea.get("id"), session["usuario_id"])
                tareas_detalle.append({
                    **tarea,
                    "paralelo": paralelo,
                    "entrega": entrega,
                })

            return render_template(
                "estudiante/tareas/listar.html",
                tareas=tareas_detalle,
                active_page="tareas_estudiante",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("dashboard_estudiante"))

    @app.route("/estudiante/tareas/<tarea_id>", methods=["GET", "POST"])
    def ver_tarea_estudiante(tarea_id):
        """Ver el detalle de la tarea y permitir la entrega."""
        if not _validar_sesion(session, "estudiante"):
            return redirect(url_for("login"))

        try:
            tarea = app.fachada.obtener_tarea(tarea_id)
            paralelo = app.fachada.obtener_paralelo_por_id(tarea.get("paralelo_id"))
            entrega = app.fachada.obtener_entrega_por_tarea_y_estudiante(tarea_id, session["usuario_id"])

            if request.method == "POST":
                archivo = request.files.get("archivo")
                comentario = request.form.get("comentario", "").strip()

                if not archivo or not archivo.filename:
                    flash("Debe seleccionar un archivo para la entrega.", "error")
                    return redirect(url_for("ver_tarea_estudiante", tarea_id=tarea_id))

                nombre_archivo = _guardar_archivo_subido(archivo)
                app.fachada.registrar_entrega(tarea_id, session["usuario_id"], nombre_archivo, comentario)
                flash("Entrega registrada correctamente.", "success")
                return redirect(url_for("ver_tarea_estudiante", tarea_id=tarea_id))

            return render_template(
                "estudiante/tareas/ver.html",
                tarea=tarea,
                paralelo=paralelo,
                entrega=entrega,
                active_page="tareas_estudiante",
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_tareas_estudiante"))

    @app.route("/uploads/<path:filename>", methods=["GET"])
    def descargar_archivo(filename):
        """Descarga un archivo subido en el sistema."""
        return send_from_directory(str(app.config["UPLOAD_FOLDER"]), filename, as_attachment=True)

    # ===================== GESTIÓN DE USUARIOS =====================

    @app.route("/usuarios", methods=["GET"])
    def listar_usuarios():
        """Listar todos los usuarios (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado. Solo administradores.", "error")
            return redirect(url_for("login"))

        # Obtener parámetros de búsqueda y filtro
        buscar = request.args.get("buscar", "").strip()
        rol_filtro = request.args.get("rol", "").strip()
        estado_filtro = request.args.get("estado", "").strip()

        try:
            # Si hay búsqueda, usarla
            if buscar:
                usuarios = app.fachada.buscar_usuarios("nombre", buscar)
            # Si hay filtro de rol
            elif rol_filtro:
                usuarios = app.fachada.listar_por_rol(rol_filtro)
            # Filtros combinados
            elif rol_filtro or estado_filtro:
                filtros = {}
                if rol_filtro:
                    filtros["rol"] = rol_filtro
                if estado_filtro == "activos":
                    filtros["activo"] = True
                elif estado_filtro == "inactivos":
                    filtros["activo"] = False
                usuarios = app.fachada.filtrar_usuarios(filtros)
            else:
                usuarios = app.fachada.listar_usuarios_activos()

            context = {
                "usuarios": usuarios,
                "total": len(usuarios),
                "buscar": buscar,
                "rol_filtro": rol_filtro,
                "estado_filtro": estado_filtro,
                "roles": ["administrador", "docente", "estudiante", "coordinador"],
            }
            return render_template("admin/usuarios/listar.html", **context)
        except Exception as e:
            flash(f"Error al listar usuarios: {str(e)}", "error")
            return redirect(url_for("dashboard_administrador"))

    @app.route("/usuarios/crear", methods=["GET", "POST"])
    def crear_usuario_admin():
        """Crear nuevo usuario (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            try:
                datos = {
                    "nombre": request.form.get("nombre", "").strip(),
                    "apellido": request.form.get("apellido", "").strip(),
                    "documento": request.form.get("documento", "").strip(),
                    "email": request.form.get("email", "").strip(),
                    "telefono": request.form.get("telefono", "").strip(),
                    "rol": request.form.get("rol", "").strip(),
                }

                # Validar campos requeridos
                if not all([datos["nombre"], datos["apellido"], datos["documento"], 
                           datos["email"], datos["rol"]]):
                    flash("Todos los campos son requeridos.", "error")
                    return redirect(url_for("crear_usuario_admin"))

                # Crear usuario a través de fachada
                resultado = app.fachada.crear_usuario(datos)

                # Obtener resultado y crear notificación con credenciales temporales para el administrador
                contrasena_temp = resultado.get("contrasena_temporal")
                correo_usuario = datos.get("email")
                usuario_creado = resultado.get("usuario") or {}
                usuario_creado_id = usuario_creado.get("id")

                try:
                    # Crear notificación interna para el administrador que realizó la acción
                    app.fachada.crear_notificacion_credencial(
                        usuario_notifica_id=session.get("usuario_id"),
                        usuario_creado_id=usuario_creado_id,
                        correo=correo_usuario,
                        contrasena_temporal=contrasena_temp,
                    )
                except Exception:
                    # No interrumpir el flujo por errores en notificaciones
                    pass

                flash(f"Usuario {datos['nombre']} creado exitosamente.", "success")
                return redirect(url_for("listar_usuarios"))

            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                flash(f"Error al crear usuario: {str(e)}", "error")

            return redirect(url_for("crear_usuario_admin"))

        roles = ["administrador", "docente", "estudiante", "coordinador"]
        return render_template("admin/usuarios/crear.html", roles=roles)

    @app.route("/usuarios/<usuario_id>/editar", methods=["GET", "POST"])
    def editar_usuario_admin(usuario_id):
        """Editar usuario (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        usuario = app.fachada.obtener_usuario_por_id(usuario_id)
        if not usuario:
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("listar_usuarios"))

        if request.method == "POST":
            try:
                datos = {
                    "nombre": request.form.get("nombre", "").strip(),
                    "apellido": request.form.get("apellido", "").strip(),
                    "email": request.form.get("email", "").strip(),
                    "telefono": request.form.get("telefono", "").strip(),
                    "rol": request.form.get("rol", "").strip(),
                }

                app.fachada.editar_usuario(usuario_id, datos)
                flash("Usuario actualizado exitosamente.", "success")
                return redirect(url_for("listar_usuarios"))

            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                flash(f"Error al editar usuario: {str(e)}", "error")

        roles = ["administrador", "docente", "estudiante", "coordinador"]
        return render_template("admin/usuarios/editar.html", usuario=usuario, roles=roles)

    @app.route("/usuarios/<usuario_id>/ver", methods=["GET"])
    def ver_usuario_admin(usuario_id):
        """Ver detalles del usuario (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        usuario = app.fachada.obtener_usuario_por_id(usuario_id)
        if not usuario:
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("listar_usuarios"))

        return render_template("admin/usuarios/ver.html", usuario=usuario)

    @app.route("/usuarios/<usuario_id>/eliminar", methods=["POST"])
    def eliminar_usuario_admin(usuario_id):
        """Eliminar usuario (borrado lógico, solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        try:
            app.fachada.eliminar_usuario(usuario_id)
            flash("Usuario eliminado exitosamente.", "success")
        except Exception as e:
            flash(f"Error al eliminar usuario: {str(e)}", "error")

        return redirect(url_for("listar_usuarios"))

    @app.route("/usuarios/<usuario_id>/activar", methods=["POST"])
    def activar_usuario_admin(usuario_id):
        """Activar usuario (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        try:
            app.fachada.activar_usuario(usuario_id)
            flash("Usuario activado exitosamente.", "success")
        except Exception as e:
            flash(f"Error al activar usuario: {str(e)}", "error")

        return redirect(url_for("listar_usuarios"))

    @app.route("/usuarios/<usuario_id>/desactivar", methods=["POST"])
    def desactivar_usuario_admin(usuario_id):
        """Desactivar usuario (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        try:
            app.fachada.desactivar_usuario(usuario_id)
            flash("Usuario desactivado exitosamente.", "success")
        except Exception as e:
            flash(f"Error al desactivar usuario: {str(e)}", "error")

        return redirect(url_for("listar_usuarios"))

    @app.route("/usuarios/importar", methods=["GET", "POST"])
    def importar_usuarios_admin():
        """Importar usuarios desde Excel o CSV (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            try:
                archivo = request.files.get("archivo")
                if not archivo:
                    flash("Debe seleccionar un archivo.", "error")
                    return redirect(url_for("importar_usuarios_admin"))

                # Validar extensión
                if not (archivo.filename.endswith(".csv") or archivo.filename.endswith(".xlsx")):
                    flash("Solo se permiten archivos CSV y XLSX.", "error")
                    return redirect(url_for("importar_usuarios_admin"))

                # Procesar archivo
                from utils.importador_usuarios import ImportadorUsuarios
                importador = ImportadorUsuarios(app.fachada)
                resultado = importador.procesar_archivo(archivo)

                flash(f"Importación completada: {resultado['exitosos']} usuarios creados, "
                      f"{resultado['errores']} errores.", "success")

                return redirect(url_for("listar_usuarios"))

            except Exception as e:
                flash(f"Error al importar usuarios: {str(e)}", "error")
                return redirect(url_for("importar_usuarios_admin"))

        return render_template("admin/usuarios/importar.html")

    @app.route("/matriculas", methods=["GET"])
    def listar_matriculas_admin():
        """Listar todas las matrículas (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado. Solo administradores.", "error")
            return redirect(url_for("login"))

        try:
            matriculas = app.fachada.listar_matriculas()
            detalle_matriculas = []
            for matricula in matriculas:
                estudiante = app.fachada.obtener_usuario_por_id(matricula.get("estudiante_id"))
                paralelo = app.fachada.obtener_paralelo_por_id(matricula.get("paralelo_id"))
                detalle_matriculas.append({
                    **matricula,
                    "estudiante": estudiante,
                    "paralelo": paralelo,
                })

            return render_template(
                "admin/matriculas/listar.html",
                matriculas=detalle_matriculas,
                active_page="matriculas",
            )
        except Exception as e:
            flash(f"Error al listar matrículas: {str(e)}", "error")
            return redirect(url_for("dashboard_administrador"))

    @app.route("/admin/reportes", methods=["GET"])
    def listar_reportes_admin():
        """Listar los reportes generados (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado. Solo administradores.", "error")
            return redirect(url_for("login"))

        try:
            reportes = app.fachada.listar_reportes()
            return render_template(
                "admin/reportes.html",
                reportes=reportes,
                active_page="reportes",
            )
        except Exception as e:
            flash(f"Error al listar reportes: {str(e)}", "error")
            return redirect(url_for("dashboard_administrador"))

    @app.route("/admin/reportes/generar", methods=["POST"])
    def generar_reporte_admin():
        """Generar un nuevo reporte académico (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado. Solo administradores.", "error")
            return redirect(url_for("login"))

        formato = request.form.get("formato", "csv").strip().lower()
        try:
            resultado = app.fachada.generar_reporte_estadisticas(session["usuario_id"], formato)
            archivo = resultado["archivo"]
            nombre = resultado["nombre"]
            tipo_contenido = (
                "text/csv"
                if formato == "csv"
                else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            return Response(
                archivo,
                mimetype=tipo_contenido,
                headers={"Content-Disposition": f"attachment; filename={nombre}"},
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_reportes_admin"))

    @app.route("/admin/reportes/<reporte_id>/descargar", methods=["GET"])
    def descargar_reporte_admin(reporte_id):
        """Descargar un reporte ya generado (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado. Solo administradores.", "error")
            return redirect(url_for("login"))

        try:
            archivo, nombre, tipo_contenido = app.fachada.descargar_reporte(reporte_id)
            return Response(
                archivo,
                mimetype=tipo_contenido,
                headers={"Content-Disposition": f"attachment; filename={nombre}"},
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("listar_reportes_admin"))

    # ===================== RUTAS DE IMPORTACIÓN DE USUARIOS =====================

    @app.route("/admin/importar-usuarios", methods=["GET"])
    def listar_importar_usuarios():
        """Página de importación de usuarios (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado. Solo administradores.", "error")
            return redirect(url_for("login"))

        try:
            return render_template(
                "admin/importar_usuarios.html",
                active_page="importar_usuarios",
            )
        except Exception as e:
            flash(f"Error al acceder a importación: {str(e)}", "error")
            return redirect(url_for("dashboard_administrador"))

    @app.route("/admin/importar-usuarios/descargar-template", methods=["GET"])
    def descargar_template_usuarios():
        """Descargar template CSV para importación (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado. Solo administradores.", "error")
            return redirect(url_for("login"))

        try:
            formato = request.args.get("formato", "csv").lower()

            if formato == "xlsx":
                contenido = app.fachada.descargar_template_xlsx()
                return Response(
                    contenido,
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=template_usuarios.xlsx"},
                )
            else:
                contenido = app.fachada.descargar_template_csv()
                return Response(
                    contenido,
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=template_usuarios.csv"},
                )
        except Exception as e:
            flash(f"Error al descargar template: {str(e)}", "error")
            return redirect(url_for("listar_importar_usuarios"))

    @app.route("/admin/importar-usuarios/procesar", methods=["POST"])
    def procesar_importacion_usuarios():
        """Procesar archivo de importación de usuarios (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado. Solo administradores.", "error")
            return redirect(url_for("login"))

        try:
            # Validar que haya archivo
            if "archivo" not in request.files:
                flash("No se proporcionó archivo.", "error")
                return redirect(url_for("listar_importar_usuarios"))

            archivo = request.files["archivo"]
            if archivo.filename == "":
                flash("No se seleccionó archivo.", "error")
                return redirect(url_for("listar_importar_usuarios"))

            # Validar extensión
            if not (archivo.filename.endswith(".csv") or archivo.filename.endswith(".xlsx")):
                flash("Solo se aceptan archivos CSV y XLSX.", "error")
                return redirect(url_for("listar_importar_usuarios"))

            # Procesar archivo
            resultado = app.fachada.importar_usuarios(archivo)

            # Obtener estadísticas formateadas
            estadisticas = app.fachada.obtener_estadisticas_importacion(resultado)

            # Guardar resultado en sesión para mostrar
            session["ultimo_resultado_importacion"] = estadisticas

            # Redirigir a página de resultados
            return render_template(
                "admin/resultado_importacion.html",
                estadisticas=estadisticas,
                active_page="importar_usuarios",
            )

        except Exception as e:
            flash(f"Error al procesar importación: {str(e)}", "error")
            return redirect(url_for("listar_importar_usuarios"))

    @app.route("/matriculas/crear", methods=["GET", "POST"])
    def crear_matricula_admin():
        """Crear una nueva matrícula (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            estudiante_id = request.form.get("estudiante_id", "").strip()
            paralelo_id = request.form.get("paralelo_id", "").strip()

            if not estudiante_id or not paralelo_id:
                flash("Estudiante y paralelo son obligatorios.", "error")
                return redirect(url_for("crear_matricula_admin"))

            try:
                app.fachada.matricular_estudiante(estudiante_id, paralelo_id)
                flash("El estudiante ha sido matriculado y su horario ya se encuentra disponible.", "success")
                return redirect(url_for("listar_matriculas_admin"))
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                flash(f"Error al matricular estudiante: {str(e)}", "error")

            return redirect(url_for("crear_matricula_admin"))

        estudiantes = app.fachada.listar_por_rol("estudiante")
        paralelos = app.fachada.listar_paralelos()
        periodos = app.fachada.listar_periodos()

        return render_template(
            "admin/matriculas/crear.html",
            estudiantes=estudiantes,
            paralelos=paralelos,
            periodos=periodos,
            active_page="matriculas",
        )

    @app.route("/matriculas/<matricula_id>", methods=["GET"])
    def ver_matricula_admin(matricula_id):
        """Ver los detalles de una matrícula (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        matricula = app.fachada.obtener_matricula_por_id(matricula_id)
        if not matricula:
            flash("Matrícula no encontrada.", "error")
            return redirect(url_for("listar_matriculas_admin"))

        estudiante = app.fachada.obtener_usuario_por_id(matricula.get("estudiante_id"))
        paralelo = app.fachada.obtener_paralelo_por_id(matricula.get("paralelo_id"))

        return render_template(
            "admin/matriculas/ver.html",
            matricula=matricula,
            estudiante=estudiante,
            paralelo=paralelo,
            active_page="matriculas",
        )

    @app.route("/matriculas/<matricula_id>/cancelar", methods=["POST"])
    def cancelar_matricula_admin(matricula_id):
        """Cancelar matrícula (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        try:
            app.fachada.cancelar_matricula(matricula_id)
            flash("Matrícula cancelada correctamente.", "success")
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al cancelar la matrícula: {str(e)}", "error")

        return redirect(url_for("listar_matriculas_admin"))

    # ===================== GESTIÓN DE PARALELOS =====================

    @app.route("/paralelos", methods=["GET"])
    def listar_paralelos_admin():
        """Listar todos los paralelos (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado. Solo administradores.", "error")
            return redirect(url_for("login"))

        try:
            paralelos = app.fachada.listar_paralelos()
            return render_template(
                "admin/paralelos/listar.html",
                paralelos=paralelos,
                active_page="paralelos",
            )
        except Exception as e:
            flash(f"Error al listar paralelos: {str(e)}", "error")
            return redirect(url_for("dashboard_administrador"))

    @app.route("/paralelos/crear", methods=["GET", "POST"])
    def crear_paralelo_admin():
        """Crear paralelo (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            try:
                datos = {
                    "nombre": request.form.get("nombre", "").strip(),
                    "curso_id": request.form.get("curso_id") or None,
                    "capacidad_maxima": request.form.get("capacidad_maxima", "").strip(),
                    "descripcion": request.form.get("descripcion", "").strip(),
                    "docente_id": request.form.get("docente_id", "") or None,
                }
                app.fachada.crear_paralelo(datos)
                flash("Paralelo creado correctamente.", "success")
                return redirect(url_for("listar_paralelos_admin"))
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                flash(f"Error al crear el paralelo: {str(e)}", "error")
            return redirect(url_for("crear_paralelo_admin"))

        docentes = app.fachada.listar_docentes()
        cursos = app.fachada.listar_cursos()
        return render_template(
            "admin/paralelos/crear.html",
            docentes=docentes,
            cursos=cursos,
            active_page="paralelos",
        )

    @app.route("/paralelos/<paralelo_id>/editar", methods=["GET", "POST"])
    def editar_paralelo_admin(paralelo_id):
        """Editar paralelo (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        paralelo = app.fachada.obtener_paralelo_por_id(paralelo_id)
        if not paralelo:
            flash("Paralelo no encontrado.", "error")
            return redirect(url_for("listar_paralelos_admin"))

        if request.method == "POST":
            try:
                datos = {
                    "nombre": request.form.get("nombre", "").strip(),
                    "curso_id": request.form.get("curso_id") or None,
                    "capacidad_maxima": request.form.get("capacidad_maxima", "").strip(),
                    "descripcion": request.form.get("descripcion", "").strip(),
                    "docente_id": request.form.get("docente_id", "") or None,
                }
                app.fachada.editar_paralelo(paralelo_id, datos)
                flash("Paralelo actualizado correctamente.", "success")
                return redirect(url_for("listar_paralelos_admin"))
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                flash(f"Error al actualizar el paralelo: {str(e)}", "error")
            return redirect(url_for("editar_paralelo_admin", paralelo_id=paralelo_id))

        docentes = app.fachada.listar_docentes()
        cursos = app.fachada.listar_cursos()
        return render_template(
            "admin/paralelos/editar.html",
            paralelo=paralelo,
            docentes=docentes,
            cursos=cursos,
            active_page="paralelos",
        )

    @app.route("/paralelos/<paralelo_id>", methods=["GET"])
    def ver_paralelo_admin(paralelo_id):
        """Ver detalles de un paralelo (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        paralelo = app.fachada.obtener_paralelo_por_id(paralelo_id)
        if not paralelo:
            flash("Paralelo no encontrado.", "error")
            return redirect(url_for("listar_paralelos_admin"))

        estudiantes_matriculados = app.fachada.listar_estudiantes_matriculados(paralelo_id)
        estudiantes_detalle = [
            {
                "matricula": matricula,
                "estudiante": app.fachada.obtener_usuario_por_id(matricula.get("estudiante_id")),
            }
            for matricula in estudiantes_matriculados
        ]
        docente = app.fachada.obtener_usuario_por_id(paralelo.get("docente_id")) if paralelo.get("docente_id") else None
        cupos_disponibles = app.fachada.consultar_cupos_disponibles(paralelo_id)

        return render_template(
            "admin/paralelos/ver.html",
            paralelo=paralelo,
            estudiantes=estudiantes_detalle,
            docente=docente,
            cupos_disponibles=cupos_disponibles,
            active_page="paralelos",
        )

    @app.route("/paralelos/<paralelo_id>/eliminar", methods=["POST"])
    def eliminar_paralelo_admin(paralelo_id):
        """Eliminar paralelo (solo admin)."""
        if not _validar_sesion(session, "administrador"):
            flash("Acceso denegado.", "error")
            return redirect(url_for("login"))

        try:
            app.fachada.eliminar_paralelo(paralelo_id)
            flash("Paralelo eliminado correctamente.", "success")
        except Exception as e:
            flash(f"Error al eliminar el paralelo: {str(e)}", "error")

        return redirect(url_for("listar_paralelos_admin"))

    # ===================== MANEJO DE ERRORES =====================

    @app.errorhandler(404)
    def error_404(error):
        """Manejo de error 404."""
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def error_500(error):
        """Manejo de error 500."""
        return render_template("errors/500.html"), 500

    @app.context_processor
    def inyectar_usuario():
        """Inyecta datos del usuario en todos los templates."""
        usuario_id = session.get("usuario_id")
        return {
            "usuario_autenticado": usuario_id is not None,
            "usuario_nombre": session.get("nombre", ""),
            "usuario_rol": session.get("rol", ""),
            "notificaciones_no_leidas": app.fachada.contar_notificaciones_no_leidas(usuario_id) if usuario_id else 0,
            "notificaciones_recientes": app.fachada.listar_notificaciones_recientes(usuario_id) if usuario_id else [],
        }


def _validar_sesion(session_data, rol_requerido=None):
    """Valida que la sesión sea válida y tenga el rol requerido."""
    if "usuario_id" not in session_data:
        return False

    if rol_requerido and session_data.get("rol") != rol_requerido:
        return False

    return True


def _archivo_permitido(nombre_archivo: str) -> bool:
    """Valida las extensiones permitidas para las cargas de archivo."""
    extensiones_permitidas = {"pdf", "docx", "zip"}
    return (
        "." in nombre_archivo
        and nombre_archivo.rsplit(".", 1)[1].lower() in extensiones_permitidas
    )


def _guardar_archivo_subido(archivo) -> str:
    """Guarda un archivo subido en el directorio de uploads y devuelve su nombre seguro."""
    if not archivo or not archivo.filename:
        raise ValueError("No se proporcionó un archivo válido.")

    if not _archivo_permitido(archivo.filename):
        raise ValueError("Solo se permiten archivos PDF, DOCX y ZIP.")

    nombre_seguro = secure_filename(archivo.filename)
    nombre_guardado = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{nombre_seguro}"
    ruta_destino = Path(app.config["UPLOAD_FOLDER"]) / nombre_guardado
    archivo.save(str(ruta_destino))
    return nombre_guardado


# Crear y registrar la aplicación
app = crear_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


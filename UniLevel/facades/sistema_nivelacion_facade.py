from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from werkzeug.datastructures import FileStorage

try:
    from observers.subject import Subject
    from observers.notificacion_observer import NotificacionObserver
    from observers.email_observer import EmailObserver
    from observers.auditoria_observer import AuditoriaObserver
    import config
except ImportError:
    from UniLevel.observers.subject import Subject
    from UniLevel.observers.notificacion_observer import NotificacionObserver
    from UniLevel.observers.email_observer import EmailObserver
    from UniLevel.observers.auditoria_observer import AuditoriaObserver
    from UniLevel import config

from services.autenticacion_service import AutenticacionService
from services.matricula_service import MatriculaService
from services.usuario_service import UsuarioService
from services.paralelo_service import ParaleloService
from services.periodo_academico_service import PeriodoAcademicoService
from services.notificacion_service import NotificacionService
from services.tarea_service import TareaService
from services.entrega_service import EntregaService
from services.calificacion_service import CalificacionService
from services.asistencia_service import AsistenciaService
from services.horario_service import HorarioService
from services.reporte_service import ReporteService
from services.importador_service import ImportadorService


class SistemaNivelacionFacade:
    """Fachada que orquesta los servicios centrales de UniLevel.

    Esta clase fue elegida como punto de integración porque reúne los servicios
    del negocio y permite emitir eventos de forma desacoplada. Gracias a Observer,
    la creación de usuarios, la matrícula, las tareas y las calificaciones pueden
    activar notificaciones, correos y auditoría sin que los servicios conozcan
    directamente a los observadores.
    """

    def __init__(
        self,
        autenticacion_service: AutenticacionService,
        usuario_service: UsuarioService,
        matricula_service: MatriculaService,
        paralelo_service: ParaleloService,
        periodo_service: PeriodoAcademicoService,
        notificacion_service: NotificacionService,
        tarea_service: TareaService,
        entrega_service: EntregaService,
        calificacion_service: CalificacionService,
        asistencia_service: AsistenciaService,
        horario_service: Optional["HorarioService"] = None,
        reporte_service: Optional["ReporteService"] = None,
        importador_service: Optional[ImportadorService] = None,
    ) -> None:
        self._autenticacion_service = autenticacion_service
        self._usuario_service = usuario_service
        self._matricula_service = matricula_service
        self._paralelo_service = paralelo_service
        self._periodo_service = periodo_service
        self._notificacion_service = notificacion_service
        self._tarea_service = tarea_service
        self._entrega_service = entrega_service
        self._calificacion_service = calificacion_service
        self._asistencia_service = asistencia_service
        self._reporte_service = reporte_service
        self._horario_service = horario_service
        self._importador_service = importador_service

        self._auditoria_path = self._obtener_auditoria_path()
        self._subject = Subject()
        self._inicializar_observers()

    def _obtener_auditoria_path(self) -> str:
        if hasattr(config, "Config") and hasattr(config.Config, "JSON_AUDITORIA"):
            return getattr(config.Config, "JSON_AUDITORIA")
        if hasattr(config, "JSON_AUDITORIA"):
            return getattr(config, "JSON_AUDITORIA")
        return str(Path(__file__).resolve().parent.parent / "data" / "auditoria.json")

    def _inicializar_observers(self) -> None:
        self._subject.agregar_observer(NotificacionObserver(self._notificacion_service))
        self._subject.agregar_observer(EmailObserver())
        self._subject.agregar_observer(AuditoriaObserver(self._auditoria_path))

    def _emitir_evento(self, evento: str, datos: Dict[str, Any]) -> None:
        if getattr(self, "_subject", None) is not None:
            self._subject.notificar(evento, datos)

    def listar_paralelos_por_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        return self._paralelo_service.listar_por_docente(docente_id)

    def listar_estudiantes_por_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        """Retorna los datos completos de los estudiantes asignados a los paralelos del docente."""
        paralelos = self._paralelo_service.listar_por_docente(docente_id)
        paralelo_ids = {p.get("id") for p in paralelos}
        matriculas = self._matricula_service.listar_matriculas()
        estudiantes_ids = {
            m.get("estudiante_id")
            for m in matriculas
            if m.get("paralelo_id") in paralelo_ids and str(m.get("estado", "")).lower() == "matriculado"
        }
        estudiantes = []
        for est_id in estudiantes_ids:
            usuario = self._usuario_service.buscar_usuario(est_id)
            if usuario is not None:
                estudiantes.append(usuario)
        return estudiantes

    def obtener_horario_por_matricula(self, matricula_id: Any) -> Optional[Dict[str, Any]]:
        if getattr(self, "_horario_service", None) is None:
            return None
        return self._horario_service.obtener_por_matricula(matricula_id)

    def iniciar_sesion(self, correo: str, password: str) -> Dict[str, Any]:
        return self._autenticacion_service.iniciar_sesion(correo, password)

    def cerrar_sesion(self) -> None:
        return self._autenticacion_service.cerrar_sesion()

    def cambiar_password(self, usuario_id: Any, nueva_password: str) -> bool:
        return self._autenticacion_service.cambiar_password(usuario_id, nueva_password)

    def crear_usuario(self, datos_usuario: Dict[str, Any]) -> Dict[str, Any]:
        resultado = self._usuario_service.crear_usuario(datos_usuario)
        self._emitir_evento("usuario_creado", {"usuario": resultado.get("usuario")})
        return resultado

    def editar_usuario(self, usuario_id: Any, datos_actualizar: Dict[str, Any]) -> bool:
        return self._usuario_service.editar_usuario(usuario_id, datos_actualizar)

    def eliminar_usuario(self, usuario_id: Any) -> bool:
        return self._usuario_service.eliminar_usuario(usuario_id)

    def activar_usuario(self, usuario_id: Any) -> bool:
        return self._usuario_service.activar_usuario(usuario_id)

    def desactivar_usuario(self, usuario_id: Any) -> bool:
        return self._usuario_service.desactivar_usuario(usuario_id)

    def obtener_usuario_por_id(self, usuario_id: Any) -> Optional[Dict[str, Any]]:
        return self._usuario_service.buscar_usuario(usuario_id)

    def listar_usuarios(self) -> List[Dict[str, Any]]:
        return self._usuario_service.listar_usuarios()

    def listar_usuarios_activos(self) -> List[Dict[str, Any]]:
        return self._usuario_service.listar_usuarios_activos()

    def listar_por_rol(self, rol: str) -> List[Dict[str, Any]]:
        return self._usuario_service.listar_por_rol(rol)

    def buscar_usuarios(self, criterio: str, valor: str) -> List[Dict[str, Any]]:
        return self._usuario_service.buscar_usuarios(criterio, valor)

    def filtrar_usuarios(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._usuario_service.filtrar_usuarios(filtros)

    def listar_estudiantes(self) -> List[Dict[str, Any]]:
        return self._usuario_service.listar_por_rol("estudiante")

    def listar_docentes(self) -> List[Dict[str, Any]]:
        return self._usuario_service.listar_por_rol("docente")

    def listar_paralelos(self) -> List[Dict[str, Any]]:
        return self._paralelo_service.listar_paralelos()

    def obtener_paralelo_por_id(self, paralelo_id: Any) -> Optional[Dict[str, Any]]:
        return self._paralelo_service.obtener_paralelo(paralelo_id)

    def crear_paralelo(self, datos_paralelo: Dict[str, Any]) -> Dict[str, Any]:
        return self._paralelo_service.crear_paralelo(datos_paralelo)

    def editar_paralelo(self, paralelo_id: Any, datos_actualizar: Dict[str, Any]) -> Dict[str, Any]:
        return self._paralelo_service.editar_paralelo(paralelo_id, datos_actualizar)

    def eliminar_paralelo(self, paralelo_id: Any) -> bool:
        return self._paralelo_service.eliminar_paralelo(paralelo_id)

    def asignar_docente_paralelo(self, paralelo_id: Any, docente_id: Any) -> Dict[str, Any]:
        paralelo = self._paralelo_service.asignar_docente(paralelo_id, docente_id)
        if docente_id:
            titulo = "Asignación de paralelo"
            mensaje = (
                f"Se te ha asignado el paralelo '{paralelo.get('curso_nombre', paralelo.get('nombre', ''))}' "
                f"con capacidad de {paralelo.get('capacidad_maxima', 'N/D')} estudiantes."
            )
            self._notificacion_service.crear_notificacion(docente_id, titulo, mensaje)
            docente = self._usuario_service.buscar_usuario(docente_id)
            evento_datos = {"paralelo": paralelo}
            if docente is not None:
                evento_datos["docente_email"] = docente.get("email")
            self._emitir_evento("docente_asignado", evento_datos)
        return paralelo

    def listar_estudiantes_matriculados(self, paralelo_id: Any) -> List[Dict[str, Any]]:
        return self._paralelo_service.listar_estudiantes_matriculados(paralelo_id)

    def consultar_cupos_disponibles(self, paralelo_id: Any) -> int:
        return self._paralelo_service.consultar_cupos_disponibles(paralelo_id)

    def listar_periodos(self) -> List[Dict[str, Any]]:
        return self._periodo_service.listar_periodos()

    def obtener_periodo_por_id(self, periodo_id: Any) -> Optional[Dict[str, Any]]:
        return self._periodo_service.obtener_periodo_por_id(periodo_id)

    def obtener_periodo_activo(self) -> Optional[Dict[str, Any]]:
        return self._periodo_service.obtener_periodo_activo()

    def listar_matriculas(self) -> List[Dict[str, Any]]:
        return self._matricula_service.listar_matriculas()

    def listar_matriculas_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        return self._matricula_service.listar_matriculas_por_estudiante(estudiante_id)

    def obtener_matricula_activa_por_estudiante(self, estudiante_id: Any) -> Optional[Dict[str, Any]]:
        return self._matricula_service.obtener_matricula_activa_por_estudiante(estudiante_id)

    def obtener_matricula_por_id(self, matricula_id: Any) -> Optional[Dict[str, Any]]:
        return self._matricula_service.obtener_matricula_por_id(matricula_id)

    def contar_notificaciones_no_leidas(self, usuario_id: Any) -> int:
        return self._notificacion_service.contar_notificaciones_no_leidas(usuario_id)

    def crear_notificacion(self, usuario_id: Any, titulo: str, mensaje: str) -> Dict[str, Any]:
        return self._notificacion_service.crear_notificacion(usuario_id, titulo, mensaje)

    def crear_notificacion_credencial(self, usuario_notifica_id: Any, usuario_creado_id: Any, correo: str, contrasena_temporal: str) -> Dict[str, Any]:
        """Crea una notificación especial para credenciales temporales asociadas a un usuario creado."""
        titulo = "Credenciales temporales generadas"
        mensaje = f"Se han generado credenciales temporales para el usuario {correo}."
        meta = {
            "tipo": "credencial_temporal",
            "usuario_id": usuario_creado_id,
            "correo": correo,
            "password_temporal": contrasena_temporal,
        }
        return self._notificacion_service.crear_notificacion_con_meta(usuario_notifica_id, titulo, mensaje, meta)

    def eliminar_notificaciones_credenciales_por_usuario(self, usuario_id: Any) -> int:
        """Elimina notificaciones de tipo 'credencial_temporal' asociadas a `usuario_id`."""
        return self._notificacion_service.eliminar_credenciales_temporales_por_usuario(usuario_id)

    def listar_notificaciones(self, usuario_id: Any) -> List[Dict[str, Any]]:
        return self._notificacion_service.listar_por_usuario(usuario_id)

    def listar_notificaciones_recientes(self, usuario_id: Any, limite: int = 5) -> List[Dict[str, Any]]:
        return self._notificacion_service.listar_recientes_por_usuario(usuario_id, limite)

    def marcar_notificacion_como_leida(self, notificacion_id: Any, usuario_id: Any) -> Dict[str, Any]:
        return self._notificacion_service.marcar_como_leida(notificacion_id, usuario_id)

    def marcar_todas_notificaciones_como_leidas(self, usuario_id: Any) -> int:
        return self._notificacion_service.marcar_todas_como_leidas(usuario_id)

    def eliminar_notificacion(self, notificacion_id: Any, usuario_id: Any) -> bool:
        return self._notificacion_service.eliminar_notificacion(notificacion_id, usuario_id)

    def listar_reportes(self) -> List[Dict[str, Any]]:
        if self._reporte_service is None:
            return []
        return self._reporte_service.listar_reportes()

    def obtener_reporte_por_id(self, reporte_id: Any) -> Dict[str, Any]:
        if self._reporte_service is None:
            raise RuntimeError("Servicio de reportes no configurado.")
        return self._reporte_service.obtener_reporte(reporte_id)

    def generar_reporte_estadisticas(self, usuario_id: Any, formato: str = "csv", criterios: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self._reporte_service is None:
            raise RuntimeError("Servicio de reportes no configurado.")
        return self._reporte_service.generar_reporte_estadisticas(usuario_id, formato, criterios)

    def descargar_reporte(self, reporte_id: Any) -> tuple[bytes, str, str]:
        if self._reporte_service is None:
            raise RuntimeError("Servicio de reportes no configurado.")
        return self._reporte_service.descargar_reporte(reporte_id)

    def marcar_notificacion_como_leida(self, notificacion_id: Any, usuario_id: Any) -> Dict[str, Any]:
        return self._notificacion_service.marcar_como_leida(notificacion_id, usuario_id)

    def marcar_todas_notificaciones_como_leidas(self, usuario_id: Any) -> int:
        return self._notificacion_service.marcar_todas_como_leidas(usuario_id)

    def eliminar_notificacion(self, notificacion_id: Any, usuario_id: Any) -> bool:
        return self._notificacion_service.eliminar_notificacion(notificacion_id, usuario_id)

    def listar_tareas_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        return self._tarea_service.listar_por_docente(docente_id)

    def listar_calificaciones_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        return self._calificacion_service.listar_por_docente(docente_id)

    def listar_calificaciones(self) -> List[Dict[str, Any]]:
        return self._calificacion_service.listar_todas_calificaciones()

    def calcular_tasa_aprobacion(self) -> float:
        return self._calificacion_service.calcular_tasa_aprobacion()

    def obtener_calificacion(self, calificacion_id: Any) -> Dict[str, Any]:
        return self._calificacion_service.obtener_calificacion(calificacion_id)

    def registrar_calificacion(self, datos_calificacion: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        calificacion = self._calificacion_service.registrar_calificacion(datos_calificacion, docente_id)
        estudiante = self._usuario_service.buscar_usuario(datos_calificacion.get("estudiante_id"))
        evento_datos = {"calificacion": calificacion}
        if estudiante is not None:
            evento_datos["estudiante_email"] = estudiante.get("email")
        self._emitir_evento("calificacion_publicada", evento_datos)
        return calificacion

    def editar_calificacion(self, calificacion_id: Any, datos_calificacion: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        return self._calificacion_service.editar_calificacion(calificacion_id, datos_calificacion, docente_id)

    def listar_calificaciones_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        return self._calificacion_service.listar_por_estudiante(estudiante_id)

    def calcular_promedio_estudiante(self, estudiante_id: Any) -> float:
        return self._calificacion_service.calcular_promedio_estudiante(estudiante_id)

    def listar_asistencias_docente(self, docente_id: Any, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return self._asistencia_service.listar_por_docente(docente_id, filtros)

    def obtener_asistencia(self, asistencia_id: Any) -> Dict[str, Any]:
        return self._asistencia_service.obtener_asistencia(asistencia_id)

    def registrar_asistencia(self, datos_asistencia: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        return self._asistencia_service.registrar_asistencia(datos_asistencia, docente_id)

    def editar_asistencia(self, asistencia_id: Any, datos_asistencia: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        return self._asistencia_service.editar_asistencia(asistencia_id, datos_asistencia, docente_id)

    # ------------------ Coordinador: Carreras / Mallas / Asignaturas / Cursos ------------------
    def listar_carreras(self) -> List[Dict[str, Any]]:
        if getattr(self, "_carrera_service", None) is None:
            return []
        return self._carrera_service.listar_carreras()

    def crear_carrera(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        if getattr(self, "_carrera_service", None) is None:
            raise RuntimeError("Servicio de carreras no configurado.")
        return self._carrera_service.crear_carrera(datos)

    def obtener_carrera(self, carrera_id: Any) -> Optional[Dict[str, Any]]:
        if getattr(self, "_carrera_service", None) is None:
            return None
        return self._carrera_service.obtener_carrera(carrera_id)

    def editar_carrera(self, carrera_id: Any, datos: Dict[str, Any]) -> bool:
        if getattr(self, "_carrera_service", None) is None:
            raise RuntimeError("Servicio de carreras no configurado.")
        return self._carrera_service.editar_carrera(carrera_id, datos)

    def eliminar_carrera(self, carrera_id: Any) -> bool:
        if getattr(self, "_carrera_service", None) is None:
            raise RuntimeError("Servicio de carreras no configurado.")
        return self._carrera_service.eliminar_carrera(carrera_id)

    def listar_mallas(self) -> List[Dict[str, Any]]:
        if getattr(self, "_malla_service", None) is None:
            return []
        return self._malla_service.listar_mallas()

    def crear_malla(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        if getattr(self, "_malla_service", None) is None:
            raise RuntimeError("Servicio de mallas no configurado.")
        return self._malla_service.crear_malla(datos)

    def obtener_malla(self, malla_id: Any) -> Optional[Dict[str, Any]]:
        if getattr(self, "_malla_service", None) is None:
            return None
        return self._malla_service.obtener_malla(malla_id)

    def editar_malla(self, malla_id: Any, datos: Dict[str, Any]) -> bool:
        if getattr(self, "_malla_service", None) is None:
            raise RuntimeError("Servicio de mallas no configurado.")
        return self._malla_service.editar_malla(malla_id, datos)

    def eliminar_malla(self, malla_id: Any) -> bool:
        if getattr(self, "_malla_service", None) is None:
            raise RuntimeError("Servicio de mallas no configurado.")
        return self._malla_service.eliminar_malla(malla_id)

    def listar_asignaturas(self) -> List[Dict[str, Any]]:
        if getattr(self, "_asignatura_service", None) is None:
            return []
        return self._asignatura_service.listar_asignaturas()

    def crear_asignatura(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        if getattr(self, "_asignatura_service", None) is None:
            raise RuntimeError("Servicio de asignaturas no configurado.")
        return self._asignatura_service.crear_asignatura(datos)

    def obtener_asignatura(self, asignatura_id: Any) -> Optional[Dict[str, Any]]:
        if getattr(self, "_asignatura_service", None) is None:
            return None
        return self._asignatura_service.obtener_asignatura(asignatura_id)

    def editar_asignatura(self, asignatura_id: Any, datos: Dict[str, Any]) -> bool:
        if getattr(self, "_asignatura_service", None) is None:
            raise RuntimeError("Servicio de asignaturas no configurado.")
        return self._asignatura_service.editar_asignatura(asignatura_id, datos)

    def eliminar_asignatura(self, asignatura_id: Any) -> bool:
        if getattr(self, "_asignatura_service", None) is None:
            raise RuntimeError("Servicio de asignaturas no configurado.")
        return self._asignatura_service.eliminar_asignatura(asignatura_id)

    def listar_cursos(self) -> List[Dict[str, Any]]:
        if getattr(self, "_curso_service", None) is None:
            return []
        return self._curso_service.listar_cursos()

    def crear_curso(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        if getattr(self, "_curso_service", None) is None:
            raise RuntimeError("Servicio de cursos no configurado.")
        return self._curso_service.crear_curso(datos)

    def obtener_curso(self, curso_id: Any) -> Optional[Dict[str, Any]]:
        if getattr(self, "_curso_service", None) is None:
            return None
        return self._curso_service.obtener_curso(curso_id)

    def editar_curso(self, curso_id: Any, datos: Dict[str, Any]) -> bool:
        if getattr(self, "_curso_service", None) is None:
            raise RuntimeError("Servicio de cursos no configurado.")
        return self._curso_service.editar_curso(curso_id, datos)

    def eliminar_curso(self, curso_id: Any) -> bool:
        if getattr(self, "_curso_service", None) is None:
            raise RuntimeError("Servicio de cursos no configurado.")
        return self._curso_service.eliminar_curso(curso_id)


    def listar_asistencias_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        return self._asistencia_service.listar_por_estudiante(estudiante_id)

    def calcular_porcentaje_asistencia_estudiante(self, estudiante_id: Any) -> float:
        return self._asistencia_service.calcular_porcentaje_asistencia_estudiante(estudiante_id)

    def obtener_tarea(self, tarea_id: Any) -> Dict[str, Any]:
        return self._tarea_service.obtener_tarea(tarea_id)

    def listar_tareas_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        return self._tarea_service.listar_tareas_para_estudiante(estudiante_id)

    def crear_tarea(self, datos_tarea: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        tarea = self._tarea_service.crear_tarea(datos_tarea, docente_id)
        docente = self._usuario_service.buscar_usuario(docente_id)
        evento_datos = {"tarea": tarea}
        if docente is not None:
            evento_datos["docente_email"] = docente.get("email")
        self._emitir_evento("tarea_creada", evento_datos)
        return tarea

    def editar_tarea(self, tarea_id: Any, datos_tarea: Dict[str, Any], docente_id: Any) -> Dict[str, Any]:
        return self._tarea_service.editar_tarea(tarea_id, datos_tarea, docente_id)

    def eliminar_tarea(self, tarea_id: Any, docente_id: Any) -> bool:
        return self._tarea_service.eliminar_tarea(tarea_id, docente_id)

    def listar_entregas_tarea(self, tarea_id: Any) -> List[Dict[str, Any]]:
        return self._entrega_service.listar_por_tarea(tarea_id)

    def listar_entregas_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        return self._entrega_service.listar_por_estudiante(estudiante_id)

    def registrar_entrega(self, tarea_id: Any, estudiante_id: Any, nombre_archivo: str, comentario: Optional[str] = None) -> Dict[str, Any]:
        return self._entrega_service.registrar_entrega(tarea_id, estudiante_id, nombre_archivo, comentario)

    def calificar_entrega(self, entrega_id: Any, docente_id: Any, puntuacion: float, comentario: Optional[str] = None) -> Dict[str, Any]:
        return self._entrega_service.calificar_entrega(entrega_id, docente_id, puntuacion, comentario)

    def obtener_entrega(self, entrega_id: Any) -> Dict[str, Any]:
        return self._entrega_service.obtener_entrega(entrega_id)

    def obtener_entrega_por_tarea_y_estudiante(self, tarea_id: Any, estudiante_id: Any) -> Optional[Dict[str, Any]]:
        return self._entrega_service.obtener_entrega_por_tarea_y_estudiante(tarea_id, estudiante_id)

    def matricular_estudiante(
        self,
        estudiante_id: Any,
        paralelo_id: Any,
        datos_extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        matricula = self._matricula_service.matricular_estudiante(estudiante_id, paralelo_id, datos_extra)
        estudiante = self._usuario_service.buscar_usuario(estudiante_id)
        evento_datos = {"matricula": matricula}
        if estudiante is not None:
            evento_datos["estudiante_email"] = estudiante.get("email")
        self._emitir_evento("estudiante_matriculado", evento_datos)
        return matricula

    def cancelar_matricula(self, matricula_id: Any) -> bool:
        return self._matricula_service.cancelar_matricula(matricula_id)

    def asignar_paralelo(self, estudiante_id: Any, paralelo_id: Any) -> Dict[str, Any]:
        return self._matricula_service.asignar_paralelo(estudiante_id, paralelo_id)

    # Métodos de Importación de Usuarios
    def importar_usuarios(self, archivo: FileStorage) -> Dict[str, Any]:
        if not self._importador_service:
            raise ValueError("Servicio de importación no disponible")
        return self._importador_service.procesar_archivo(archivo)

    def descargar_template_csv(self) -> str:
        if not self._importador_service:
            raise ValueError("Servicio de importación no disponible")
        return self._importador_service.generar_template_csv()

    def descargar_template_xlsx(self) -> bytes:
        if not self._importador_service:
            raise ValueError("Servicio de importación no disponible")
        return self._importador_service.generar_template_xlsx()

    def obtener_estadisticas_importacion(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        if not self._importador_service:
            raise ValueError("Servicio de importación no disponible")
        return self._importador_service.obtener_estadisticas_importacion(resultado)

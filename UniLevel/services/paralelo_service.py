from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from repositories.matricula_repository import MatriculaRepository
from repositories.paralelo_repository import ParaleloRepository
from services.curso_service import CursoService


class ParaleloService:
    """Servicio responsable de la gestión de paralelos."""

    def __init__(
        self,
        paralelo_repository: ParaleloRepository,
        matricula_repository: Optional[MatriculaRepository] = None,
        curso_service: Optional[CursoService] = None,
    ) -> None:
        self._paralelo_repository = paralelo_repository
        self._matricula_repository = matricula_repository
        self._curso_service = curso_service

    def listar_paralelos(self) -> List[Dict[str, Any]]:
        """Retorna todos los paralelos con estado y cupos actualizados."""
        return [self._actualizar_estado(paralelo) for paralelo in self._paralelo_repository.obtener_todos()]

    def obtener_paralelo(self, paralelo_id: Any) -> Dict[str, Any]:
        """Obtiene un paralelo por su identificador y actualiza su estado."""
        paralelo = self._paralelo_repository.obtener_por_id(paralelo_id)
        if paralelo is None:
            raise ValueError("Paralelo no encontrado.")

        return self._actualizar_estado(paralelo)

    def crear_paralelo(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo paralelo validando la información solicitada."""
        self._validar_datos_basicos(datos)

        capacidad_maxima = int(datos["capacidad_maxima"])
        curso_id = datos.get("curso_id") or None
        curso = self._obtener_curso(curso_id) if curso_id else None

        paralelo = {
            "id": str(uuid.uuid4()),
            "nombre": datos["nombre"].strip(),
            "curso_id": curso_id,
            "asignatura_id": curso.get("asignatura_id") if curso else None,
            "malla_id": curso.get("malla_id") if curso else None,
            "docente_id": datos.get("docente_id") or None,
            "capacidad_maxima": capacidad_maxima,
            "descripcion": datos.get("descripcion", "").strip(),
            "estado": "Disponible",
        }

        if curso is not None:
            paralelo["curso_nombre"] = curso.get("nombre")

        paralelo_guardado = self._paralelo_repository.guardar(paralelo)
        return self._actualizar_estado(paralelo_guardado)

    def editar_paralelo(self, paralelo_id: Any, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Edita un paralelo existente y recalcula su estado."""
        paralelo = self._paralelo_repository.obtener_por_id(paralelo_id)
        if paralelo is None:
            raise ValueError("Paralelo no encontrado.")

        actualizacion: Dict[str, Any] = {}
        if "nombre" in datos and datos["nombre"]:
            actualizacion["nombre"] = datos["nombre"].strip()
        if "descripcion" in datos:
            actualizacion["descripcion"] = datos.get("descripcion", "").strip()
        if "capacidad_maxima" in datos and datos["capacidad_maxima"] is not None:
            capacidad_nueva = int(datos["capacidad_maxima"])
            inscritos = self.contar_inscritos(paralelo_id)
            if capacidad_nueva < inscritos:
                raise ValueError(
                    "La capacidad no puede ser menor que los estudiantes ya matriculados."
                )
            actualizacion["capacidad_maxima"] = capacidad_nueva
        if "docente_id" in datos:
            actualizacion["docente_id"] = datos.get("docente_id") or None
        if "curso_id" in datos:
            curso_id = datos.get("curso_id") or None
            curso = self._obtener_curso(curso_id) if curso_id else None
            actualizacion["curso_id"] = curso_id
            actualizacion["asignatura_id"] = curso.get("asignatura_id") if curso else None
            actualizacion["malla_id"] = curso.get("malla_id") if curso else None
            actualizacion["curso_nombre"] = curso.get("nombre") if curso else None

        if not actualizacion:
            return self.obtener_paralelo(paralelo_id)

        actualizado = self._paralelo_repository.actualizar(paralelo_id, actualizacion)
        if not actualizado:
            raise RuntimeError("No fue posible actualizar el paralelo.")

        return self.obtener_paralelo(paralelo_id)

    def eliminar_paralelo(self, paralelo_id: Any) -> bool:
        """Elimina un paralelo si no tiene estudiantes matriculados."""
        if self.contar_inscritos(paralelo_id) > 0:
            raise ValueError("No se puede eliminar un paralelo con estudiantes matriculados.")

        if not self._paralelo_repository.existe_paralelo(paralelo_id):
            raise ValueError("Paralelo no encontrado.")

        return self._paralelo_repository.eliminar(paralelo_id)

    def asignar_docente(self, paralelo_id: Any, docente_id: Any) -> Dict[str, Any]:
        """Asigna un docente a un paralelo sin duplicar la asignación."""
        paralelo = self._paralelo_repository.obtener_por_id(paralelo_id)
        if paralelo is None:
            raise ValueError("Paralelo no encontrado.")

        if paralelo.get("docente_id") == docente_id:
            return self.obtener_paralelo(paralelo_id)

        actualizado = self._paralelo_repository.actualizar(paralelo_id, {"docente_id": docente_id})
        if not actualizado:
            raise RuntimeError("No fue posible asignar el docente al paralelo.")

        return self.obtener_paralelo(paralelo_id)

    def listar_estudiantes_matriculados(self, paralelo_id: Any) -> List[Dict[str, Any]]:
        """Devuelve las matrículas activas asociadas a un paralelo."""
        if self._matricula_repository is None:
            return []

        return [
            matricula
            for matricula in self._matricula_repository.buscar_por_paralelo(paralelo_id)
            if isinstance(matricula, dict)
            and str(matricula.get("estado", "")).lower() == "matriculado"
        ]

    def listar_por_docente(self, docente_id: Any) -> List[Dict[str, Any]]:
        """Lista los paralelos asignados a un docente."""
        return [
            self._actualizar_estado(paralelo)
            for paralelo in self._paralelo_repository.obtener_todos()
            if isinstance(paralelo, dict) and paralelo.get("docente_id") == docente_id
        ]

    def contar_inscritos(self, paralelo_id: Any) -> int:
        """Cuenta cuántos estudiantes están matriculados en un paralelo."""
        return len(self.listar_estudiantes_matriculados(paralelo_id))

    def consultar_cupos_disponibles(self, paralelo_id: Any) -> int:
        """Retorna la cantidad de cupos libres en el paralelo."""
        paralelo = self.obtener_paralelo(paralelo_id)
        capacidad_maxima = int(paralelo.get("capacidad_maxima", 0))
        disponibles = capacidad_maxima - self.contar_inscritos(paralelo_id)
        return max(disponibles, 0)

    def _validar_datos_basicos(self, datos: Dict[str, Any]) -> None:
        """Valida los campos básicos de un paralelo."""
        if not datos.get("nombre"):
            raise ValueError("El nombre del paralelo es obligatorio.")
        if not datos.get("curso_id"):
            raise ValueError("El curso del paralelo es obligatorio.")
        if not datos.get("capacidad_maxima"):
            raise ValueError("La capacidad máxima es obligatoria.")
        try:
            capacidad = int(datos["capacidad_maxima"])
            if capacidad <= 0:
                raise ValueError("La capacidad máxima debe ser mayor que cero.")
        except (TypeError, ValueError):
            raise ValueError("La capacidad máxima debe ser un número entero válido.")

    def _actualizar_estado(self, paralelo: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza el estado del paralelo según los cupos disponibles."""
        if not isinstance(paralelo, dict):
            return paralelo

        paralelo = {**paralelo}
        inscritos = self.contar_inscritos(paralelo.get("id"))
        capacidad_maxima = int(paralelo.get("capacidad_maxima", 0))
        paralelo["inscritos"] = inscritos
        paralelo["cupos_disponibles"] = max(capacidad_maxima - inscritos, 0)
        paralelo["estado"] = "Sin Cupos" if inscritos >= capacidad_maxima else "Disponible"
        paralelo["porcentaje_ocupacion"] = (
            min(int((inscritos / capacidad_maxima) * 100), 100) if capacidad_maxima > 0 else 0
        )

        if self._curso_service is not None and paralelo.get("curso_id"):
            curso = self._curso_service.obtener_curso(paralelo.get("curso_id"))
            if curso:
                paralelo["curso"] = curso
                paralelo["curso_nombre"] = paralelo.get("curso_nombre") or curso.get("nombre")
                paralelo["asignatura_nombre"] = paralelo.get("asignatura_nombre") or curso.get("nombre")
                paralelo["malla_id"] = paralelo.get("malla_id") or curso.get("malla_id")

        return paralelo

    def _obtener_curso(self, curso_id: Any) -> Dict[str, Any]:
        if self._curso_service is None:
            raise ValueError("Servicio de cursos no configurado para validar el paralelo.")
        curso = self._curso_service.obtener_curso(curso_id)
        if curso is None:
            raise ValueError("Curso no encontrado.")
        return curso

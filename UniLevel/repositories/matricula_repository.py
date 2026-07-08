from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class MatriculaRepository(BaseRepository):
    """Repositorio para la persistencia de matrículas en archivos JSON."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todas las matrículas almacenadas."""
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene una matrícula por su identificador."""
        for matricula in self.obtener_todos():
            if isinstance(matricula, dict) and matricula.get("id") == id:
                return matricula
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda una nueva matrícula en el repositorio."""
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        """Actualiza una matrícula existente."""
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        """Elimina una matrícula por su identificador."""
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

    def buscar_por_estudiante(self, estudiante_id: Any) -> List[Dict[str, Any]]:
        """Busca matrículas asociadas a un estudiante."""
        return [
            matricula
            for matricula in self.obtener_todos()
            if isinstance(matricula, dict) and matricula.get("estudiante_id") == estudiante_id
        ]

    def buscar_por_paralelo(self, paralelo_id: Any) -> List[Dict[str, Any]]:
        """Busca matrículas asociadas a un paralelo."""
        return [
            matricula
            for matricula in self.obtener_todos()
            if isinstance(matricula, dict) and matricula.get("paralelo_id") == paralelo_id
        ]

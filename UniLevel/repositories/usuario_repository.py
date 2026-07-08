from __future__ import annotations

from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    """Repositorio para la persistencia de usuarios en archivos JSON."""

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios almacenados."""
        return self._json_manager.leer_archivo(self._ruta_archivo)

    def obtener_por_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su identificador único."""
        for usuario in self.obtener_todos():
            if isinstance(usuario, dict) and usuario.get("id") == id:
                return usuario
        return None

    def guardar(self, objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda un nuevo usuario en el repositorio."""
        return self._json_manager.agregar_elemento(self._ruta_archivo, objeto)

    def actualizar(self, id: Any, objeto: Dict[str, Any]) -> bool:
        """Actualiza un usuario existente por id."""
        return self._json_manager.actualizar_elemento(self._ruta_archivo, id, objeto)

    def eliminar(self, id: Any) -> bool:
        """Elimina un usuario por su identificador."""
        return self._json_manager.eliminar_elemento(self._ruta_archivo, id)

    def guardar_usuario(self, usuario: Dict[str, Any]) -> Dict[str, Any]:
        """Método específico para guardar un usuario."""
        return self.guardar(usuario)

    def buscar_por_correo(self, correo: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por correo electrónico."""
        for usuario in self.obtener_todos():
            if isinstance(usuario, dict) and usuario.get("email") == correo:
                return usuario
        return None

    def buscar_por_cedula(self, cedula: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por número de cédula."""
        for usuario in self.obtener_todos():
            if isinstance(usuario, dict) and usuario.get("documento") == cedula:
                return usuario
        return None

    def listar_por_rol(self, rol: str) -> List[Dict[str, Any]]:
        """Lista usuarios filtrados por rol."""
        return [usuario for usuario in self.obtener_todos() 
                if isinstance(usuario, dict) and usuario.get("rol") == rol]

    def buscar_por_criterio(self, criterio: str, valor: str) -> List[Dict[str, Any]]:
        """Busca usuarios por criterio (nombre, email, documento, rol)."""
        resultado = []
        valor_lower = valor.lower()
        
        for usuario in self.obtener_todos():
            if not isinstance(usuario, dict):
                continue
            
            if criterio == "nombre":
                if valor_lower in usuario.get("nombre", "").lower():
                    resultado.append(usuario)
            elif criterio == "email":
                if valor_lower in usuario.get("email", "").lower():
                    resultado.append(usuario)
            elif criterio == "documento":
                if valor_lower in usuario.get("documento", "").lower():
                    resultado.append(usuario)
            elif criterio == "rol":
                if usuario.get("rol") == valor:
                    resultado.append(usuario)
        
        return resultado

    def filtrar(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filtra usuarios según múltiples criterios."""
        resultado = self.obtener_todos()
        
        # Filtrar por rol
        if "rol" in filtros:
            resultado = [u for u in resultado if u.get("rol") == filtros["rol"]]
        
        # Filtrar por activo
        if "activo" in filtros:
            resultado = [u for u in resultado if u.get("activo", True) == filtros["activo"]]
        
        # Filtrar por eliminado
        if "eliminado" in filtros:
            resultado = [u for u in resultado if u.get("eliminado", False) == filtros["eliminado"]]
        
        return resultado

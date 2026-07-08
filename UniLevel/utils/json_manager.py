import json
import os
from typing import Any, Dict, List


class JsonManager:
    """Manejador centralizado de archivos JSON para UniLevel.

    Esta clase centraliza la lectura y escritura de datos con formato JSON.
    Los repositorios pueden reutilizar esta implementación para persistencia.
    """

    @staticmethod
    def _crear_archivo_si_no_existe(ruta: str) -> None:
        """Crea el archivo JSON con una lista vacía si no existe."""
        if not os.path.exists(ruta):
            try:
                os.makedirs(os.path.dirname(ruta), exist_ok=True)
                with open(ruta, "w", encoding="utf-8") as archivo:
                    json.dump([], archivo, ensure_ascii=False, indent=4)
            except OSError as error:
                raise IOError(f"No se pudo crear el archivo JSON: {error}")

    @classmethod
    def leer_archivo(cls, ruta: str) -> List[Dict[str, Any]]:
        """Lee y devuelve el contenido de un archivo JSON como una lista de diccionarios."""
        cls._crear_archivo_si_no_existe(ruta)

        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                contenido = json.load(archivo)
                if not isinstance(contenido, list):
                    raise ValueError("El archivo JSON debe contener una lista de elementos.")
                return contenido
        except (json.JSONDecodeError, ValueError) as error:
            cls.guardar_archivo(ruta, [])
            return []
        except OSError as error:
            raise IOError(f"Error leyendo el archivo JSON: {error}")

    @staticmethod
    def guardar_archivo(ruta: str, datos: List[Dict[str, Any]]) -> None:
        """Guarda una lista de diccionarios en un archivo JSON."""
        try:
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
        except OSError as error:
            raise IOError(f"Error guardando el archivo JSON: {error}")

    @classmethod
    def agregar_elemento(cls, ruta: str, elemento: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega un nuevo elemento a la lista JSON y lo guarda en el archivo."""
        elementos = cls.leer_archivo(ruta)
        elementos.append(elemento)
        cls.guardar_archivo(ruta, elementos)
        return elemento

    @classmethod
    def actualizar_elemento(
        cls,
        ruta: str,
        id: Any,
        datos_actualizados: Dict[str, Any],
    ) -> bool:
        """Actualiza un elemento existente identificado por su id."""
        elementos = cls.leer_archivo(ruta)
        actualizado = False

        for indice, elemento in enumerate(elementos):
            if isinstance(elemento, dict) and elemento.get("id") == id:
                elementos[indice] = {**elemento, **datos_actualizados}
                actualizado = True
                break

        if actualizado:
            cls.guardar_archivo(ruta, elementos)

        return actualizado

    @classmethod
    def eliminar_elemento(cls, ruta: str, id: Any) -> bool:
        """Elimina un elemento identificado por su id del archivo JSON."""
        elementos = cls.leer_archivo(ruta)
        elementos_filtrados = [elemento for elemento in elementos if not (isinstance(elemento, dict) and elemento.get("id") == id)]

        if len(elementos_filtrados) == len(elementos):
            return False

        cls.guardar_archivo(ruta, elementos_filtrados)
        return True

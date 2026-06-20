"""
Factory para crear usuarios del sistema.
Este patrón centraliza la lógica de creación de usuarios, facilitando
el mantenimiento y la extensión del código.
"""

from .estudiante import Estudiante
from .docente import Docente
from .administrador import Administrador
from .coordinador import Coordinador


class UsuarioFactory:
    """
    Factory para crear usuarios de diferentes tipos.
    
    Uso:
        usuario = UsuarioFactory.crear_usuario(
            tipo="estudiante",
            nombre="Alexander",
            apellido="Erazo",
            email="ale@gmail.com",
            password="0000",
            matricula="A1",
            carrera="ISF"
        )
    """
    
    @staticmethod
    def crear_usuario(tipo, nombre, apellido, email, password, **kwargs):
        """
        Crea un usuario del tipo especificado.
        
        Parámetros:
            tipo (str): Tipo de usuario ('estudiante', 'docente', 'admin', 'coordinador')
            nombre (str): Nombre del usuario
            apellido (str): Apellido del usuario
            email (str): Email del usuario
            password (str): Contraseña del usuario
            **kwargs: Argumentos adicionales según el tipo:
                - Para estudiante: matricula, carrera
                - Para docente: asignatura
        
        Retorna:
            Persona: Una instancia del tipo de usuario especificado
            
        Lanza:
            ValueError: Si el tipo de usuario no es válido
        """
        
        if tipo.lower() == "estudiante":
            return Estudiante(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=password,
                matricula=kwargs.get('matricula'),
                carrera=kwargs.get('carrera')
            )
        
        elif tipo.lower() == "docente":
            return Docente(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=password,
                especialidad=kwargs.get('asignatura') or kwargs.get('especialidad')
            )
        
        elif tipo.lower() == "admin":
            return Administrador(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=password
            )
        
        elif tipo.lower() == "coordinador":
            return Coordinador(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=password
            )
        
        else:
            raise ValueError(
                f"Tipo de usuario inválido: {tipo}. "
                f"Debe ser uno de: 'estudiante', 'docente', 'admin', 'coordinador'"
            )

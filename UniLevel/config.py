"""
config.py - Configuración de la aplicación Flask UniLevel.

Define variables de configuración para desarrollo, testing y producción.
"""

import os
from pathlib import Path


class Config:
    """Configuración base de la aplicación."""

    # Directorio base del proyecto
    BASE_DIR = Path(__file__).parent

    # Configuración de Flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora

    # Configuración de archivos
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    UPLOAD_FOLDER.mkdir(exist_ok=True)

    # Configuración de JSON
    JSON_USUARIOS = str(DATA_DIR / "usuarios.json")
    JSON_MATRICULAS = str(DATA_DIR / "matriculas.json")
    JSON_PARALELOS = str(DATA_DIR / "paralelos.json")
    JSON_PERIODOS = str(DATA_DIR / "periodos_academicos.json")
    JSON_TAREAS = str(DATA_DIR / "tareas.json")
    JSON_ENTREGAS = str(DATA_DIR / "entregas_tareas.json")
    JSON_CALIFICACIONES = str(DATA_DIR / "calificaciones.json")
    JSON_ASISTENCIAS = str(DATA_DIR / "asistencias.json")
    JSON_NOTIFICACIONES = str(DATA_DIR / "notificaciones.json")
    JSON_HORARIOS = str(DATA_DIR / "horarios.json")
    JSON_CARRERAS = str(DATA_DIR / "carreras.json")
    JSON_MALLAS = str(DATA_DIR / "mallas.json")
    JSON_ASIGNATURAS = str(DATA_DIR / "asignaturas.json")
    JSON_CURSOS = str(DATA_DIR / "cursos_nivelacion.json")
    JSON_REPORTES = str(DATA_DIR / "reportes.json")
    JSON_AUDITORIA = str(DATA_DIR / "auditoria.json")
    REPORTES_FOLDER = str(UPLOAD_FOLDER / "reportes")

    # Crear directorio de datos y subcarpetas si no existan
    DATA_DIR.mkdir(exist_ok=True)
    Path(REPORTES_FOLDER).mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""

    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción."""

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY")


class TestingConfig(Config):
    """Configuración para testing."""

    TESTING = True
    DEBUG = True
    SESSION_TYPE = "null"


# Seleccionar configuración según el entorno
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(env=None):
    """Obtiene la configuración según el entorno."""
    if env is None:
        env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])


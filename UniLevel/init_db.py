"""
init_db.py - Inicializa la base de datos con datos de prueba.

Este script crea usuarios de prueba con diferentes roles para facilitar
el testing del sistema de autenticación y autorización.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from UniLevel.repositories.usuario_repository import UsuarioRepository
from UniLevel.services.usuario_service import UsuarioService
from UniLevel.services.notificacion_service import NotificacionService
from UniLevel.utils.password_generator import PasswordGenerator
from UniLevel.utils.email_sender import EmailSender


def inicializar_datos_prueba():
    """Crea usuarios de prueba para el sistema."""

    # Inicializar repositorios y servicios
    usuario_repo = UsuarioRepository("data/usuarios.json")
    password_gen = PasswordGenerator()
    email_sender = EmailSender()
    notificacion_service = NotificacionService()

    usuario_service = UsuarioService(
        usuario_repo, notificacion_service, password_gen, email_sender
    )

    # Usuarios de prueba
    usuarios_prueba = [
        {
            "nombre": "Admin",
            "apellido": "Sistema",
            "documento": "1000000000",
            "email": "admin@unilevel.edu",
            "telefono": "5550001000",
            "rol": "administrador",
        },
        {
            "nombre": "Prof.",
            "apellido": "García",
            "documento": "2000000000",
            "email": "docente@unilevel.edu",
            "telefono": "5550002000",
            "rol": "docente",
        },
        {
            "nombre": "Juan",
            "apellido": "Pérez",
            "documento": "3000000000",
            "email": "estudiante@unilevel.edu",
            "telefono": "5550003000",
            "rol": "estudiante",
        },
        {
            "nombre": "Coord.",
            "apellido": "López",
            "documento": "4000000000",
            "email": "coordinador@unilevel.edu",
            "telefono": "5550004000",
            "rol": "coordinador",
        },
    ]

    usuarios_creados = 0
    usuarios_existentes = 0

    print("\n" + "=" * 60)
    print("🔧 INICIALIZANDO DATOS DE PRUEBA")
    print("=" * 60 + "\n")

    for datos in usuarios_prueba:
        try:
            # Verificar si el usuario ya existe
            usuario_existente = usuario_repo.buscar_por_correo(datos["email"])
            if usuario_existente:
                print(f"⏭️  {datos['email']} - Ya existe")
                usuarios_existentes += 1
                continue

            # Crear usuario con contraseña temporal conocida para pruebas
            resultado = usuario_service.crear_usuario(datos, contrasena_temporal="password123")
            usuario_id = resultado["usuario"]["id"]

            print(f"✅ {datos['email']}")
            print(f"   ID: {usuario_id}")
            print(f"   Rol: {datos['rol']}")
            print(f"   Contraseña temporal: password123 (debe ser cambiada en primer inicio)\n")

            usuarios_creados += 1

        except ValueError as e:
            print(f"❌ {datos['email']} - Error: {str(e)}\n")
        except Exception as e:
            print(f"❌ {datos['email']} - Error inesperado: {str(e)}\n")

    # Resumen
    print("=" * 60)
    print(f"✅ Usuarios creados: {usuarios_creados}")
    print(f"⏭️  Usuarios existentes: {usuarios_existentes}")
    print("=" * 60)

    print("\n📝 NOTAS IMPORTANTES:")
    print("- Todos los usuarios tienen contraseña temporal: password123")
    print("- Deben cambiarla en el primer inicio de sesión")
    print("- Los usuarios de prueba pueden usarse para testing")
    print("\n🚀 Puedes iniciar la aplicación con:")
    print("   python -m Flask run")
    print("   o")
    print("   python app.py")
    print("\n✨ Luego accede a: http://localhost:5000/login\n")


if __name__ == "__main__":
    try:
        inicializar_datos_prueba()
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        sys.exit(1)

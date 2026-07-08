Reporte de cambios UI/UX - Módulo Notificaciones y Creación de Usuarios

Fecha: 2026-06-28

Resumen:
Se implementaron mejoras en la experiencia de usuario solicitadas:

1) Mensaje al crear usuario
- Se eliminó la visualización directa de credenciales en los mensajes `flash`.
- Las credenciales temporales ahora se guardan en notificaciones internas del administrador que crea el usuario.
- Las notificaciones contienen metadatos `meta` con: `tipo: credencial_temporal`, `usuario_id`, `correo`, `password_temporal`.
- Al cambiar la contraseña en el primer inicio, se eliminan las notificaciones que contienen la contraseña temporal para ese usuario.

2) Corrección del panel de notificaciones
- Se corrigió el renderizado y la responsividad del panel de notificaciones:
  - ancho adaptable (`min(360px, 90vw)`)
  - scroll vertical si hay muchas notificaciones (`max-height: 60vh; overflow-y:auto`)
  - word-wrap y overflow-wrap para textos largos
  - tratamiento especial para notificaciones de credenciales: bloque con estilo monospace para contraseña temporal

Archivos modificados / añadidos:
- Modificados:
  - UniLevel/app.py
    - Se cambió la ruta `/usuarios/crear` para no mostrar credenciales en `flash` y crear notificación segura.
    - Se actualizó la ruta `/cambiar-password` para eliminar notificaciones de credenciales temporales al cambiar la contraseña.
  - UniLevel/services/notificacion_service.py
    - Añadidos métodos `crear_notificacion_con_meta` y `eliminar_credenciales_temporales_por_usuario`.
  - UniLevel/facades/sistema_nivelacion_facade.py
    - Añadidos wrappers `crear_notificacion_credencial` y `eliminar_notificaciones_credenciales_por_usuario`.
  - UniLevel/templates/notificaciones.html
    - Mejoras CSS y renderizado de mensajes (soporta `meta.tipo == 'credencial_temporal'`).
  - UniLevel/templates/components/notificaciones_dropdown.html
    - Dropdown responsive y word-wrap en mensajes.

- Añadidos:
  - UniLevel/REPORTE_UI_UX.md (este archivo)

Mejoras implementadas (detallado):
- Flujo seguro para credenciales temporales: el administrador consulta las credenciales desde su panel de notificaciones internas; las credenciales no aparecen en mensajes flash.
- Eliminación segura de credenciales temporales: cuando el usuario cambia su contraseña se eliminan las notificaciones que contienen la contraseña temporal asociada a ese usuario.
- Diseño responsive del panel de notificaciones: ancho adaptable, scroll vertical y manejo de textos largos, manteniendo estilos de Bootstrap.
- Visualización específica para notificaciones de tipo `credencial_temporal` con formato legible y contraseña en monospace.

Componentes corregidos:
- Servicio de notificaciones (`NotificacionService`): métodos de creación con metadatos y limpieza de credenciales temporales.
- Fachada (`SistemaNivelacionFacade`): wrappers para crear/eliminar notificaciones de credenciales.
- Rutas de la app (`app.py`): creación de usuarios y cambio de contraseña.
- Templates: `notificaciones.html` y `components/notificaciones_dropdown.html`.

Siguientes pasos recomendados:
- Probar el flujo completo en ejecución local: crear usuario (como administrador), verificar la notificación en el dropdown y en la vista completa, luego iniciar sesión como el nuevo usuario y cambiar la contraseña; comprobar que la notificación con la contraseña temporal desaparece.
- Ajustar niveles de acceso: permitir que solo administradores vean estas notificaciones.
- Enviar credenciales por correo: integrar la cola de correo (ya existe la preparación del envío en `UsuarioService`) y activar envío seguro.

Si quieres, ejecuto la aplicación y realizo la prueba end-to-end creando un usuario de prueba y mostrando las notificaciones. Si prefieres, también puedo mejorar el diseño visual del bloque de credenciales en la notificación (colores, iconos, aviso de seguridad).
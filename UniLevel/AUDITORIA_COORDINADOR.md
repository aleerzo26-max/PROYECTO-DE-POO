Auditoría del Módulo Coordinador

Fecha: 2026-06-28

Resumen de la auditoría:
Se realizó una verificación completa sobre rutas, templates, enlaces en el sidebar, opciones del dashboard, errores de `url_for`, permisos por rol y métodos implementados pero no accesibles. Se aplicaron correcciones para asegurar que las funcionalidades del Coordinador (Carreras, Mallas, Asignaturas, Cursos, Paralelos, Asignación de Docentes) sean visibles y accesibles desde la interfaz.

1) Rutas Flask encontradas relacionadas con Coordinador:
- /dashboard/coordinador -> `dashboard_coordinador`
- /coordinador/carreras -> `listar_carreras`
- /coordinador/carreras/crear -> `crear_carrera`
- /coordinador/carreras/<id>/editar -> `editar_carrera`
- /coordinador/carreras/<id>/eliminar -> `eliminar_carrera`
- /coordinador/mallas -> `listar_mallas`
- /coordinador/mallas/crear -> `crear_malla`
- /coordinador/mallas/<id>/editar -> `editar_malla`
- /coordinador/mallas/<id>/eliminar -> `eliminar_malla`
- /coordinador/asignaturas -> `listar_asignaturas`
- /coordinador/asignaturas/crear -> `crear_asignatura`
- /coordinador/asignaturas/<id>/editar -> `editar_asignatura`
- /coordinador/asignaturas/<id>/eliminar -> `eliminar_asignatura`
- /coordinador/cursos -> `listar_cursos`
- /coordinador/cursos/crear -> `crear_curso`
- /coordinador/cursos/<id>/editar -> `editar_curso`
- /coordinador/cursos/<id>/eliminar -> `eliminar_curso`
- /coordinador/paralelos -> `listar_paralelos_coordinador` (añadida)
- /coordinador/paralelos/<id>/asignar -> `asignar_docente_paralelo_coordinador` (añadida)

2) Templates encontrados:
- templates/coordinador/dashboard_coordinador.html
- templates/coordinador/carreras_listar.html
- templates/coordinador/carreras_form.html
- templates/coordinador/mallas_listar.html
- templates/coordinador/mallas_form.html
- templates/coordinador/asignaturas_listar.html
- templates/coordinador/asignaturas_form.html
- templates/coordinador/cursos_listar.html
- templates/coordinador/cursos_form.html
- templates/coordinador/paralelos_listar.html (añadida)
- templates/coordinador/paralelos_asignar.html (añadida)

3) Enlaces en el sidebar / navbar para Coordinador:
- Se añadió un dropdown en la navbar cuando `usuario_rol == 'coordinador'` con enlaces a:
  - Dashboard (/dashboard/coordinador)
  - Carreras (/coordinador/carreras)
  - Mallas (/coordinador/mallas)
  - Asignaturas (/coordinador/asignaturas)
  - Cursos (/coordinador/cursos)
  - Paralelos (/coordinador/paralelos)

4) Opciones mostradas en el dashboard del coordinador:
- Estadísticas (Estudiantes, Cursos, Docentes, Tasa de Aprobación)
- Panel de Control con botones para:
  - Crear/Ver Cursos
  - Gestionar Matrículas
  - Ver Reportes
  - Cronograma (apunta a Paralelos)
  - Notificaciones
  - Ver Carreras, Ver Mallas, Ver Asignaturas, Ver Paralelos (agregados)
- Cursos Activos
- Perfil y Pendientes

5) Errores de `url_for()` detectados:
- Se detectó una referencia previa a `listar_periodos` en el template del dashboard que no existía como endpoint. Fue corregida apuntando a `listar_paralelos_coordinador`.
- No se detectaron otros `url_for` faltantes después de las correcciones.

6) Errores de permisos por rol:
- Antes, las rutas de gestión de paralelos eran solo para administradores (`/paralelos`), por lo que el coordinador no podía acceder ni asignar docentes. Se añadieron rutas específicas para coordinador que permiten:
  - Listar paralelos (`/coordinador/paralelos`)
  - Asignar docente a paralelo (`/coordinador/paralelos/<id>/asignar`)
  - Estas rutas verifican `session['rol'] == 'coordinador'`.

7) Métodos implementados pero no accesibles:
- La funcionalidad de asignar docentes existía en servicios/fachada (`asignar_docente_paralelo`) pero no tenía rutas accesibles para coordinador. Se expuso mediante las rutas añadidas.

Correcciones realizadas automáticamente:
- Añadidas rutas coordinador para paralelos y asignación de docentes.
- Añadidos templates `paralelos_listar.html` y `paralelos_asignar.html`.
- Añadido dropdown en la navbar para coordinador con enlaces rápidos.
- Actualizados botones del `dashboard_coordinador` para apuntar a rutas reales y añadidos botones para Carreras, Mallas, Asignaturas y Paralelos.
- Corregido `url_for('listar_periodos')` inexistente.

Estado final:
- Funcionalidades visibles: Carreras, Mallas, Asignaturas, Cursos, Paralelos (listado y asignación desde coordinador).
- Funcionalidades ocultas: Gestión completa de matrículas y paralelos (creación/edición/eliminación) siguen siendo responsabilidad del rol administrador; si deseas permitir al coordinador más acciones (crear/editar/eliminar paralelos o matriculas), lo implemento como rutas con validación de rol.

Archivos creados/modificados (resumen):
- Modificados: `app.py`, `templates/layouts/base.html`, `templates/coordinador/dashboard_coordinador.html`, (varios templates de notificaciones ya modificados en tarea previa)
- Añadidos: `templates/coordinador/paralelos_listar.html`, `templates/coordinador/paralelos_asignar.html`

Recomendación:
- Si deseas que el coordinador pueda crear/editar/eliminar paralelos o gestionar matrículas directamente, indicar qué operaciones permitir y lo implemento con las validaciones necesarias.

Fin del informe.

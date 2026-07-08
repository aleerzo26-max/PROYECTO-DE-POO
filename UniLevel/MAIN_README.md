# 🧪 Pruebas de Arquitectura - main.py

## 📋 Descripción

El archivo `main.py` es un cliente de consola para pruebas interactivas de la arquitectura completa del sistema UniLevel **sin Flask**.

## 🎯 Objetivo

Validar que toda la arquitectura funciona correctamente antes de integrar las interfaces gráficas y Flask.

## 🚀 Cómo Ejecutar

```bash
cd UniLevel
python main.py
```

## 📌 Componentes Inicializados

### Repositorios
- `UsuarioRepository` → `data/usuarios.json`
- `MatriculaRepository` → `data/matriculas.json`
- `ParaleloRepository` → `data/paralelos.json`
- `TareaRepository` → `data/tareas.json`
- `CalificacionRepository` → `data/calificaciones.json`
- `AsistenciaRepository` → `data/asistencias.json`

### Servicios
- `AutenticacionService` (iniciar sesión, cambiar contraseña)
- `UsuarioService` (crear, editar, listar usuarios)
- `MatriculaService` (matricular, cancelar matrícula)
- `NotificacionService` (crear notificaciones)

### Fachada
- `SistemaNivelacionFacade` - Orquesta todos los servicios

## 📱 Menú de Opciones

```
1. Crear usuario
   - Solicita: Nombre, Apellido, Documento, Email, Teléfono, Rol
   - Valida: Que no exista usuario con mismo documento/email
   - Genera: Contraseña temporal
   
2. Iniciar sesión
   - Solicita: Correo, Contraseña
   - Valida: Credenciales
   - Guarda: Usuario autenticado en sesión
   
3. Matricular estudiante
   - Solicita: ID estudiante, ID paralelo
   - Valida: Cupo disponible, estudiante no duplicado
   
4. Crear paralelo
   - Solicita: Nombre, Asignatura, ID docente, Capacidad
   - Almacena: En paralelos.json
   
5. Crear tarea
   - Solicita: Título, Descripción, Asignatura, ID paralelo, Fecha entrega
   - Almacena: En tareas.json
   
6. Registrar calificación
   - Solicita: ID estudiante, ID tarea, Puntuación (0-10)
   - Valida: Rango válido
   
7. Ver usuarios
   - Lista: Todos los usuarios registrados con detalles
   
8. Ver estudiantes
   - Lista: Solo usuarios con rol "estudiante"
   
9. Ver docentes
   - Lista: Solo usuarios con rol "docente"
   
10. Salir
    - Finaliza el programa
```

## 💡 Ejemplo de Uso

### Paso 1: Crear usuarios de prueba
```
Opción: 1
Nombre: Juan
Apellido: Pérez
Documento: 1234567890
Email: juan@example.com
Teléfono: 5551234567
Rol: estudiante
✅ Usuario creado: [id-generado]
```

### Paso 2: Iniciar sesión
```
Opción: 2
Correo: juan@example.com
Contraseña: [contraseña temporal mostrada al crear usuario]
✅ Sesión iniciada como: Juan Pérez
```

### Paso 3: Crear un paralelo
```
Opción: 4
Nombre: A
Asignatura: Matemáticas
ID del docente: [id-del-docente]
Capacidad máxima: 30
✅ Paralelo creado: [id-generado]
```

### Paso 4: Matricular estudiante
```
Opción: 3
ID del estudiante: [id-juan]
ID del paralelo: [id-paralelo]
✅ Estudiante matriculado correctamente
```

## 📊 Archivos de Datos Generados

Los datos se almacenan en `data/` en archivos JSON:

```
data/
├── usuarios.json          (Usuarios del sistema)
├── matriculas.json        (Registros de matrícula)
├── paralelos.json         (Paralelos/secciones)
├── tareas.json           (Tareas académicas)
├── calificaciones.json   (Calificaciones)
├── asistencias.json      (Registros de asistencia)
└── notificaciones.json   (Notificaciones)
```

## ✅ Validaciones Implementadas

- ✅ Usuario único por documento y email
- ✅ Rol válido (administrador/docente/estudiante/coordinador)
- ✅ Cupo disponible en paralelos
- ✅ Estudiante no duplicado en paralelo
- ✅ Puntuación entre 0-10
- ✅ Credenciales válidas para login

## 🎓 Roles Disponibles

- `administrador` - Acceso total al sistema
- `docente` - Gestión de tareas y calificaciones
- `estudiante` - Visualización y entrega de tareas
- `coordinador` - Supervisión de matrículas y paralelos

## 🔐 Seguridad

- Contraseñas hasheadas con SHA-256
- Validación de primer inicio de sesión
- Contraseñas temporales generadas automáticamente
- Cambio obligatorio de contraseña en primer inicio

## 📝 Notas Importantes

1. **Sin Flask**: Este archivo NO usa Flask, solo consola
2. **Inyección de Dependencias**: Todos los servicios reciben dependencias en constructor
3. **Fachada**: Solo se usa `SistemaNivelacionFacade` para operaciones
4. **Datos Persistentes**: Todos los datos se guardan en JSON
5. **Pruebas**: Está listo para validar toda la arquitectura antes de UI

## 🐛 Manejo de Errores

Todos los errores se capturan y muestran con formato:
```
❌ Error: Descripción del error
```

Los errores comunes incluyen:
- Usuario ya existe
- Credenciales inválidas
- Cambio de contraseña obligatorio
- Cupo no disponible
- Datos inválidos

## 🔄 Próximos Pasos

Una vez validada la arquitectura con este archivo, se puede:
1. ✅ Integrar Flask para crear rutas HTTP
2. ✅ Crear templates HTML
3. ✅ Implementar sistema de sesiones
4. ✅ Agregar interfaz gráfica
5. ✅ Integrar base de datos real si es necesario

---
**Estado**: ✅ Listo para pruebas
**Última actualización**: 2026-06-23

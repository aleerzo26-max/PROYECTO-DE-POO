# ⚡ INICIO RÁPIDO

## 🚀 Ejecución Inmediata

### Opción 1: Pruebas Automatizadas (Recomendado para validar)
```bash
cd c:\Users\usuario\Documents\PROYECTO-DE-POO
python UniLevel/test_automatizado.py
```
**Resultado esperado**: ✅ 7/7 pruebas exitosas

---

### Opción 2: Menú Interactivo (Para explorar)
```bash
cd c:\Users\usuario\Documents\PROYECTO-DE-POO
python UniLevel/main.py
```
**Resultado esperado**: Menú interactivo con 10 opciones

---

## 📋 Menú Principal (main.py)

```
===== SISTEMA UNILEVEL =====

1. Crear usuario              → Crear nuevo usuario (admin/docente/estudiante/coordinador)
2. Iniciar sesión             → Login con email y contraseña
3. Matricular estudiante      → Matricular en un paralelo
4. Crear paralelo             → Crear nueva sección de curso
5. Crear tarea                → Crear tarea académica
6. Registrar calificación     → Registrar calificación de tarea
7. Ver usuarios               → Listar todos los usuarios
8. Ver estudiantes            → Listar solo estudiantes
9. Ver docentes               → Listar solo docentes
10. Salir                     → Finalizar programa
```

---

## 📊 Ejemplo de Flujo Completo

### Paso 1: Crear Docente
```
Opción: 1
Nombre: María
Apellido: González
Documento: 1111111111
Email: maria@unilevel.edu
Teléfono: 5551234567
Rol: docente
✅ Usuario creado: [id-generado]
```

### Paso 2: Crear Estudiante
```
Opción: 1
Nombre: Juan
Apellido: Pérez
Documento: 2222222222
Email: juan@unilevel.edu
Teléfono: 5559876543
Rol: estudiante
✅ Usuario creado: [id-generado]
```

### Paso 3: Crear Paralelo
```
Opción: 4
Nombre: A
Asignatura: Matemáticas
ID del docente: [id-maria]
Capacidad máxima: 30
✅ Paralelo creado: [id-generado]
```

### Paso 4: Matricular Estudiante
```
Opción: 3
ID del estudiante: [id-juan]
ID del paralelo: [id-paralelo]
✅ Estudiante matriculado correctamente
```

### Paso 5: Crear Tarea
```
Opción: 5
Título de la tarea: Algebra Lineal - Ejercicios 1-10
Descripción: Resolver ejercicios del capítulo 3
Asignatura: Matemáticas
ID del paralelo: [id-paralelo]
Fecha de entrega (YYYY-MM-DD): 2026-07-01
✅ Tarea creada: [id-generado]
```

### Paso 6: Registrar Calificación
```
Opción: 6
ID del estudiante: [id-juan]
ID de la tarea: [id-tarea]
Puntuación (0-10): 8.5
✅ Calificación registrada: [id-generado]
```

### Paso 7: Ver Resultados
```
Opción: 7
--- USUARIOS REGISTRADOS ---

Total de usuarios: 2

ID: [id-maria]
  Nombre: María González
  Email: maria@unilevel.edu
  Rol: docente

ID: [id-juan]
  Nombre: Juan Pérez
  Email: juan@unilevel.edu
  Rol: estudiante
```

---

## ✅ Validaciones Automáticas

El sistema valida automáticamente:
- ✅ No permite usuarios con mismo documento
- ✅ No permite usuarios con mismo email
- ✅ No permite rol inválido
- ✅ No permite más estudiantes que capacidad del paralelo
- ✅ No permite calificación fuera de rango (0-10)
- ✅ No permite matricular estudiante duplicado en paralelo

---

## 📁 Archivos de Datos

Los datos se guardan automáticamente en:
```
UniLevel/data/
├── usuarios.json           ← Usuarios del sistema
├── matriculas.json         ← Matrículas
├── paralelos.json          ← Paralelos/secciones
├── tareas.json             ← Tareas
├── calificaciones.json     ← Calificaciones
└── asistencias.json        ← Asistencia
```

**Nota**: Los datos persisten entre ejecuciones.

---

## 🔑 Contraseñas Temporales

Al crear un usuario, se genera automáticamente:
- ✅ Contraseña temporal segura (12 caracteres aleatorios)
- ✅ Usuario debe cambiarla en primer inicio de sesión
- ✅ Todas las contraseñas se hashean con SHA-256

---

## 🆘 Mensajes Comunes

| Símbolo | Significado |
|---------|-------------|
| ✅ | Operación exitosa |
| ❌ | Error en la operación |
| 🚀 | Inicio del programa |
| 👋 | Fin del programa |

---

## 🐛 Troubleshooting

### Error: "ImportError: attempted relative import"
**Solución**: Ejecutar desde el directorio correcto:
```bash
cd c:\Users\usuario\Documents\PROYECTO-DE-POO
python UniLevel/main.py
```

### Error: "NotificacionService() takes no arguments"
**Solución**: Ya está corregido en la última versión

### Datos no se guardan
**Verificar**: Que el directorio `data/` exista
```bash
mkdir UniLevel\data
```

---

## 📚 Documentación Completa

Para más detalles, ver:
- `UniLevel/MAIN_README.md` - Guía completa de uso
- `UniLevel/RESUMEN_FINAL.md` - Resumen del proyecto
- `UniLevel/README.md` - Información general del proyecto

---

## � OPCIÓN 3: Aplicación Web con Flask (NUEVA!)

```bash
cd c:\Users\usuario\Documents\PROYECTO-DE-POO\UniLevel
pip install -r requirements.txt
python init_db.py
python app.py
```

**Acceso**: http://localhost:5000

### Usuarios Web (Creados por init_db.py)
```
Admin:       admin@unilevel.edu
Docente:     docente@unilevel.edu
Estudiante:  estudiante@unilevel.edu
Coordinador: coordinador@unilevel.edu

Contraseña: password123 (cambiar en primer inicio)
```

---

## 🎯 Próximos Pasos

Una vez validado el sistema:
1. ✅ Validar backend con test_automatizado.py
2. ✅ Explorar menú interactivo con main.py
3. ✅ **NUEVO**: Acceder a web Flask
4. Implementar gestión de usuarios CRUD
5. Conectar dashboards con datos reales
6. Agregar más módulos académicos

---

**¿Listo para empezar?**

### Opción Recomendada (Completo):
```bash
# 1. Validar sistema
python UniLevel/test_automatizado.py

# 2. Iniciar web
python UniLevel/init_db.py
python UniLevel/app.py
```

---
**Última actualización**: 2026-06-23
**Estado**: Flask Web ✅ Implementado

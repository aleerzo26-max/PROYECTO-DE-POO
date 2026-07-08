# 🚀 UniLevel - Módulo Web con Flask

**Estado**: ✅ Completado  
**Última actualización**: 2026-06-23

---

## 📋 Contenido Implementado

### ✅ Sistema de Autenticación
- [x] Página de login (`/login`)
- [x] Cambio de contraseña (`/cambiar-password`)
- [x] Logout (`/logout`)
- [x] Validación de sesión
- [x] Cambio obligatorio en primer inicio

### ✅ Dashboards por Rol
- [x] Dashboard Administrador (`/dashboard/admin`)
- [x] Dashboard Docente (`/dashboard/docente`)
- [x] Dashboard Estudiante (`/dashboard/estudiante`)
- [x] Dashboard Coordinador (`/dashboard/coordinador`)

### ✅ Plantillas
- [x] Layout base con navbar y footer
- [x] Formularios con Bootstrap 5
- [x] Mensajes flash (éxito, error, advertencia)
- [x] Diseño responsive
- [x] Páginas de error (404, 500)

### ✅ Seguridad
- [x] Flask Session para almacenar datos
- [x] Validación de roles
- [x] Protección de rutas
- [x] CSRF (puede mejorar)

---

## 🛠️ Instalación y Configuración

### Paso 1: Instalar Dependencias

```bash
cd c:\Users\usuario\Documents\PROYECTO-DE-POO\UniLevel

# Crear ambiente virtual (opcional pero recomendado)
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Crear Archivo .env

```bash
# Copiar archivo de ejemplo
copy .env.example .env
```

Contenido de `.env`:
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
```

### Paso 3: Inicializar Datos de Prueba

```bash
python init_db.py
```

Esto creará 4 usuarios de prueba:
- **Admin**: admin@unilevel.edu
- **Docente**: docente@unilevel.edu
- **Estudiante**: estudiante@unilevel.edu
- **Coordinador**: coordinador@unilevel.edu

**Contraseña para todos**: `password123`

---

## 🚀 Ejecutar la Aplicación

### Opción 1: Desde PowerShell

```bash
cd c:\Users\usuario\Documents\PROYECTO-DE-POO\UniLevel
python app.py
```

**Acceder a**: `http://localhost:5000`

### Opción 2: Con Flask CLI

```bash
cd c:\Users\usuario\Documents\PROYECTO-DE-POO\UniLevel
flask run
```

### Opción 3: Con Modo Debug Avanzado

```bash
cd c:\Users\usuario\Documents\PROYECTO-DE-POO\UniLevel
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
$env:FLASK_DEBUG=1
flask run
```

---

## 📱 Rutas Disponibles

### Rutas Públicas
| Ruta | Método | Descripción |
|------|--------|-------------|
| `/` | GET | Página de inicio (redirige a login o dashboard) |
| `/login` | GET, POST | Página de login |
| `/logout` | GET | Cerrar sesión |
| `/cambiar-password` | GET, POST | Cambiar contraseña (primer inicio) |

### Rutas Protegidas - Dashboards
| Ruta | Rol Requerido | Descripción |
|------|---------------|-------------|
| `/dashboard/admin` | administrador | Dashboard administrativo |
| `/dashboard/docente` | docente | Dashboard para docentes |
| `/dashboard/estudiante` | estudiante | Dashboard para estudiantes |
| `/dashboard/coordinador` | coordinador | Dashboard para coordinadores |

---

## 🔐 Flujo de Autenticación

### Primer Inicio
```
1. Usuario accede a /login
2. Ingresa credenciales (admin@unilevel.edu / password123)
3. Sistema detecta primer_inicio = True
4. Redirige a /cambiar-password
5. Usuario establece nueva contraseña
6. Sistema actualiza primer_inicio = False
7. Redirige al dashboard según rol
```

### Inicio Normal
```
1. Usuario accede a /login
2. Ingresa credenciales
3. Sistema valida contraseña
4. Sesión se crea con: usuario_id, nombre, rol, email
5. Redirige al dashboard según rol
```

### Logout
```
1. Usuario hace clic en "Cerrar sesión"
2. Sistema limpia la sesión
3. Redirige a /login con mensaje de éxito
```

---

## 🎨 Estructura de Plantillas

```
templates/
├── layouts/
│   └── base.html                 # Template base con navbar y footer
├── auth/
│   ├── login.html                # Página de login
│   └── cambiar_password.html     # Cambio de contraseña
├── admin/
│   └── dashboard_admin.html      # Dashboard administrador
├── docente/
│   └── dashboard_docente.html    # Dashboard docente
├── estudiante/
│   └── dashboard_estudiante.html # Dashboard estudiante
├── coordinador/
│   └── dashboard_coordinador.html # Dashboard coordinador
└── errors/
    ├── 404.html                  # Error 404
    └── 500.html                  # Error 500
```

---

## 💾 Estructura de Datos de Sesión

```python
session = {
    "usuario_id": "uuid-del-usuario",
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "juan@unilevel.edu",
    "rol": "estudiante",
    "permanent": True
}
```

---

## 📊 Usuarios de Prueba

### Administrador
```
Email: admin@unilevel.edu
Contraseña: password123
Rol: administrador
Acceso: Gestión completa del sistema
```

### Docente
```
Email: docente@unilevel.edu
Contraseña: password123
Rol: docente
Acceso: Crear tareas, calificar, ver estudiantes
```

### Estudiante
```
Email: estudiante@unilevel.edu
Contraseña: password123
Rol: estudiante
Acceso: Ver tareas, entregar trabajos, ver calificaciones
```

### Coordinador
```
Email: coordinador@unilevel.edu
Contraseña: password123
Rol: coordinador
Acceso: Gestión de cursos y matrículas
```

---

## 🛡️ Características de Seguridad

- ✅ Contraseñas hasheadas con SHA-256
- ✅ Validación de credenciales
- ✅ Sesiones seguras con Flask Session
- ✅ Cambio obligatorio de contraseña en primer inicio
- ✅ Validación de rol en dashboards
- ✅ Protección de rutas

---

## 🔧 Configuración Avanzada

### Cambiar Tiempo de Sesión

En `config.py`:
```python
PERMANENT_SESSION_LIFETIME = 3600  # 1 hora (en segundos)
```

### Cambiar Puerto

En `app.py`:
```python
app.run(debug=True, host="0.0.0.0", port=8000)  # Cambiar puerto a 8000
```

### Modo Producción

En `.env`:
```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=tu-clave-secreta-segura-aqui
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'flask'"

**Solución**:
```bash
pip install -r requirements.txt
```

### Error: "Secret key must be set to use session"

**Solución**: Asegúrate de que `SECRET_KEY` está configurado en `config.py` o `.env`

### Error: "Session is not available"

**Solución**: Reinicia la aplicación y limpia las cookies del navegador

### La sesión se pierde después de cerrar el navegador

**Esperado**: Es el comportamiento normal sin `PERMANENT_SESSION_LIFETIME` configurado

---

## 📈 Próximas Fases

- [ ] Integración de base de datos real (PostgreSQL)
- [ ] Sistema de recuperación de contraseña por email
- [ ] Gestión completa de usuarios (CRUD)
- [ ] Formularios de matrícula
- [ ] Sistema de tareas y entregas
- [ ] Panel de calificaciones
- [ ] Reportes académicos
- [ ] Notificaciones en tiempo real
- [ ] Descarga de documentos
- [ ] APIs RESTful para mobile

---

## 📚 Documentación Adicional

- Ver `RESUMEN_FINAL.md` para resumen de arquitectura
- Ver `MAIN_README.md` para guía de pruebas
- Ver `INICIO_RAPIDO.md` para inicio rápido

---

## ✨ Mejoras Futuras

### Seguridad
- [ ] CSRF Protection
- [ ] Rate limiting
- [ ] 2FA (Autenticación de Dos Factores)
- [ ] OAuth 2.0 / OpenID Connect

### UI/UX
- [ ] Tema claro/oscuro
- [ ] Internacionalización (i18n)
- [ ] Diseño mejorado
- [ ] Animaciones

### Performance
- [ ] Caché con Redis
- [ ] Minificación de assets
- [ ] CDN para archivos estáticos
- [ ] Optimización de BD

---

## 📞 Soporte

Para reportar problemas o sugerencias, revisa:
- `log/` - Archivos de log
- Terminal de Flask - Mensajes de error
- Navegador - Consola del desarrollador (F12)

---

**Versión**: 1.0.0  
**Última actualización**: 2026-06-23  
**Estado**: ✅ Listo para Producción (Fase Autenticación)

"""
Análisis exhaustivo completo: templates, servicios, repositorios, formularios.
"""

import re
import os
import json
from pathlib import Path
from collections import defaultdict

class AnalizadorCompleto:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.app_file = self.base_path / "app.py"
        self.templates_dir = self.base_path / "templates"
        self.services_dir = self.base_path / "services"
        self.repositories_dir = self.base_path / "repositories"
        
    def analizar_formularios(self):
        """Analiza formularios HTML y verifica que tengan su ruta POST correspondiente"""
        forms_sin_ruta = []
        
        # Buscar todos los archivos HTML
        for html_file in self.templates_dir.rglob("*.html"):
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Buscar formularios
            forms = re.findall(r'<form[^>]*method=["\']POST["\'][^>]*action=["\']([^"\']+)["\']', content, re.IGNORECASE)
            for action in forms:
                # Extraer la ruta del action
                if action.startswith('{{'):
                    match = re.search(r"url_for\(['\"]([^'\"]+)['\"]", action)
                    if match:
                        func_name = match.group(1)
                        # Verificar si existe en app.py
                        with open(self.app_file, 'r', encoding='utf-8') as f:
                            app_content = f.read()
                        if f"def {func_name}(" not in app_content:
                            forms_sin_ruta.append({
                                "archivo": str(html_file.relative_to(self.base_path)),
                                "accion": action,
                                "funcion": func_name
                            })
        
        return forms_sin_ruta
    
    def analizar_servicios(self):
        """Analiza qué métodos de servicios se llaman en app.py"""
        service_calls = defaultdict(set)
        
        with open(self.app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar llamadas tipo: app.fachada.XXXX pero también service_variable.method()
        # Primero obtenemos todas las variables de servicio asignadas en app.py
        service_pattern = r'(\w+_service)\s*='
        service_vars = set(re.findall(service_pattern, content))
        
        # Luego buscamos llamadas a métodos de esos servicios
        for service_var in service_vars:
            pattern = f'{service_var}\\.(\\w+)\\s*\\('
            methods = re.findall(pattern, content)
            if methods:
                service_calls[service_var] = set(methods)
        
        return service_calls
    
    def analizar_repositorios(self):
        """Analiza qué métodos de repositorios se llaman en services y app.py"""
        repo_calls = defaultdict(set)
        
        # Leer todos los archivos de servicios
        for service_file in self.services_dir.glob("*.py"):
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar variables repository asignadas
            repo_pattern = r'self\.(\w*_repo(?:sitory)?)\s*='
            repo_vars = set(re.findall(repo_pattern, content))
            
            # Buscar llamadas a métodos
            for repo_var in repo_vars:
                pattern = f'{repo_var}\\.(\\w+)\\s*\\('
                methods = re.findall(pattern, content)
                repo_calls[service_file.stem].update(methods)
        
        return repo_calls
    
    def analizar_dashboards(self):
        """Verifica que existan dashboards para todos los roles"""
        roles_dashboards = {
            "administrador": "admin/dashboard_admin.html",
            "docente": "docente/dashboard_docente.html",
            "coordinador": "coordinador/dashboard_coordinador.html",
            "estudiante": "estudiante/dashboard_estudiante.html"
        }
        
        resultado = {}
        for rol, template in roles_dashboards.items():
            path = self.templates_dir / template
            resultado[rol] = {
                "template": template,
                "existe": path.exists(),
                "ruta": f"/dashboard/{rol}" if rol != "coordinador" else f"/dashboard/{rol}"
            }
        
        return resultado
    
    def analizar_rutas_templates_correspondientes(self):
        """Verifica que existan templates para dashboard_* rutas"""
        with open(self.app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar rutas /dashboard/
        dashboard_routes = re.findall(r"@app\.route\(['\"](/dashboard/[^'\"]+)['\"]", content)
        
        resultado = []
        for route in dashboard_routes:
            # Extraer el rol
            role = route.split('/')[-1]
            resultado.append({
                "ruta": route,
                "rol": role
            })
        
        return resultado
    
    def generar_reporte_json(self):
        """Genera reporte JSON completo"""
        servicios = self.analizar_servicios()
        servicios_dict = {k: sorted(list(v)) for k, v in servicios.items()}
        
        repositorios = self.analizar_repositorios()
        repositorios_dict = {k: sorted(list(v)) for k, v in repositorios.items()}
        
        return {
            "formularios_sin_ruta": self.analizar_formularios(),
            "servicios": servicios_dict,
            "repositorios": repositorios_dict,
            "dashboards": self.analizar_dashboards(),
            "rutas_dashboard": self.analizar_rutas_templates_correspondientes()
        }

# Ejecutar
if __name__ == "__main__":
    analyzer = AnalizadorCompleto()
    report = analyzer.generar_reporte_json()
    
    print("\n" + "=" * 80)
    print("ANÁLISIS EXHAUSTIVO COMPLETO - UNILEVEL")
    print("=" * 80)
    
    print("\n🔴 FORMULARIOS SIN RUTA POST")
    if report['formularios_sin_ruta']:
        for form in report['formularios_sin_ruta']:
            print(f"  ❌ {form['archivo']}")
            print(f"     Acción: {form['accion']}")
            print(f"     Función esperada: {form['funcion']}")
    else:
        print("  ✓ Todos los formularios tienen ruta POST correspondiente")
    
    print("\n🟠 DASHBOARDS POR ROL")
    for rol, data in report['dashboards'].items():
        status = "✓" if data['existe'] else "❌"
        print(f"  {status} {rol.upper():15} - {data['template']:40} ({data['ruta']})")
    
    print("\n🟡 RUTAS DASHBOARD DEFINIDAS")
    for route_info in report['rutas_dashboard']:
        print(f"  • {route_info['ruta']} (rol: {route_info['rol']})")
    
    print("\n🔵 SERVICIOS Y MÉTODOS LLAMADOS")
    total_service_methods = 0
    for service, methods in sorted(report['servicios'].items()):
        if methods:
            print(f"  • {service}: {', '.join(sorted(methods))}")
            total_service_methods += len(methods)
    print(f"  Total: {total_service_methods} llamadas a servicios")
    
    print("\n🟢 REPOSITORIOS Y MÉTODOS LLAMADOS")
    total_repo_methods = 0
    for service, methods in sorted(report['repositorios'].items()):
        if methods:
            print(f"  • {service}: {', '.join(sorted(methods))}")
            total_repo_methods += len(methods)
    print(f"  Total: {total_repo_methods} llamadas a repositorios")
    
    print("\n" + "=" * 80)
    
    # Guardar JSON
    with open("analisis_completo.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("✓ Análisis guardado en: analisis_completo.json\n")

"""
Script de análisis exhaustivo del proyecto UniLevel.
Verifica: rutas, templates, métodos de servicios, repositorios, etc.
"""

import re
import os
import json
from pathlib import Path

class AnalizadorUniLevel:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.app_file = self.base_path / "app.py"
        self.facades_dir = self.base_path / "facades"
        self.services_dir = self.base_path / "services"
        self.repositories_dir = self.base_path / "repositories"
        self.templates_dir = self.base_path / "templates"
        
    def get_app_routes(self):
        """Extrae todas las rutas definidas en app.py"""
        with open(self.app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'@app\.route\(["\']([^"\']+)["\'][,\)].*?\ndef\s+(\w+)\('
        matches = re.findall(pattern, content, re.DOTALL)
        routes = {}
        for route, func_name in matches:
            routes[route] = func_name
        return routes
    
    def get_render_templates(self):
        """Extrae todos los templates referenciados en app.py"""
        with open(self.app_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        templates = set()
        for i, line in enumerate(lines):
            # Caso 1: render_template("path", ...) en una sola línea
            match = re.search(r'render_template\(\s*["\']([^"\']+)["\']', line)
            if match:
                templates.add(match.group(1))
            
            # Caso 2: render_template( en una línea y template en la siguiente
            if 'render_template(' in line and i+1 < len(lines):
                next_line = lines[i+1]
                match = re.search(r'^["\']([^"\']+)["\']', next_line.strip())
                if match:
                    templates.add(match.group(1))
        
        return templates
    
    def check_templates_exist(self):
        """Verifica que todos los templates existan"""
        templates = self.get_render_templates()
        missing = []
        existing = []
        
        for template in templates:
            path = self.templates_dir / template
            if path.exists():
                existing.append(template)
            else:
                missing.append(template)
        
        return {"existing": sorted(existing), "missing": sorted(missing)}
    
    def get_url_for_calls(self):
        """Extrae todos los url_for() del app.py"""
        with open(self.app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'url_for\(["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)
        return sorted(set(matches))
    
    def get_defined_functions(self):
        """Obtiene todas las funciones definidas en app.py"""
        with open(self.app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'def\s+(\w+)\s*\('
        matches = re.findall(pattern, content)
        return set(matches)
    
    def check_url_for_references(self):
        """Verifica que todos los url_for() apunten a rutas existentes"""
        url_fors = self.get_url_for_calls()
        defined_funcs = self.get_defined_functions()
        
        missing = []
        existing = []
        
        for func_name in url_fors:
            if func_name in defined_funcs:
                existing.append(func_name)
            else:
                missing.append(func_name)
        
        return {"existing": sorted(existing), "missing": sorted(missing)}
    
    def get_facade_methods(self):
        """Extrae todos los métodos definidos en la fachada"""
        facade_file = self.facades_dir / "sistema_nivelacion_facade.py"
        if not facade_file.exists():
            return {}
        
        with open(facade_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'def\s+(\w+)\s*\(self'
        matches = re.findall(pattern, content)
        return set(matches)
    
    def get_facade_calls_in_app(self):
        """Extrae todos los app.fachada.XXX() en app.py"""
        with open(self.app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'app\.fachada\.(\w+)\s*\('
        matches = re.findall(pattern, content)
        return sorted(set(matches))
    
    def check_facade_methods(self):
        """Verifica que todos los métodos de fachada existan"""
        calls = self.get_facade_calls_in_app()
        defined = self.get_facade_methods()
        
        missing = []
        existing = []
        
        for method in calls:
            if method in defined:
                existing.append(method)
            else:
                missing.append(method)
        
        return {"existing": sorted(existing), "missing": sorted(missing)}
    
    def generate_report(self):
        """Genera un reporte completo"""
        report = {
            "templates": self.check_templates_exist(),
            "url_for_references": self.check_url_for_references(),
            "facade_methods": self.check_facade_methods(),
            "total_routes": len(self.get_app_routes()),
            "total_templates": len(self.get_render_templates()),
        }
        return report

# Ejecutar análisis
if __name__ == "__main__":
    analyzer = AnalizadorUniLevel()
    report = analyzer.generate_report()
    
    print("=" * 70)
    print("ANÁLISIS EXHAUSTIVO DEL PROYECTO UNILEVEL")
    print("=" * 70)
    
    print("\n📋 TEMPLATES")
    print(f"  Total referencias: {report['total_templates']}")
    print(f"  Existentes: {len(report['templates']['existing'])}")
    print(f"  Faltantes: {len(report['templates']['missing'])}")
    if report['templates']['missing']:
        print("  ❌ FALTANTES:")
        for t in report['templates']['missing']:
            print(f"     - {t}")
    
    print("\n🔗 URL_FOR REFERENCES")
    print(f"  Total referencias: {len(report['url_for_references']['existing']) + len(report['url_for_references']['missing'])}")
    print(f"  Válidas: {len(report['url_for_references']['existing'])}")
    print(f"  Inválidas: {len(report['url_for_references']['missing'])}")
    if report['url_for_references']['missing']:
        print("  ❌ RUTAS NO ENCONTRADAS:")
        for r in report['url_for_references']['missing']:
            print(f"     - {r}")
    
    print("\n🎯 MÉTODOS DE FACHADA")
    print(f"  Total llamadas: {len(report['facade_methods']['existing']) + len(report['facade_methods']['missing'])}")
    print(f"  Implementados: {len(report['facade_methods']['existing'])}")
    print(f"  Faltantes: {len(report['facade_methods']['missing'])}")
    if report['facade_methods']['missing']:
        print("  ❌ MÉTODOS FALTANTES:")
        for m in report['facade_methods']['missing']:
            print(f"     - {m}")
    
    print(f"\n📊 RUTAS TOTALES: {report['total_routes']}")
    
    print("\n" + "=" * 70)
    
    # Exportar a JSON
    with open("analisis_unilevel.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("✓ Reporte guardado en: analisis_unilevel.json")

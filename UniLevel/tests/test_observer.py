import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from observers.auditoria_observer import AuditoriaObserver


class ObserverTests(unittest.TestCase):
    def test_auditoria_registra_descripcion_y_evento(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta_auditoria = os.path.join(tmpdir, "auditoria.json")
            observer = AuditoriaObserver(ruta_auditoria)
            observer.update(
                "usuario_creado",
                {"usuario": {"id": "u1", "nombre": "Ana", "apellido": "Lopez"}},
            )

            with open(ruta_auditoria, "r", encoding="utf-8") as handle:
                registros = handle.read()

            self.assertIn('"evento": "usuario_creado"', registros)
            self.assertIn('"descripcion":', registros)


if __name__ == "__main__":
    unittest.main()

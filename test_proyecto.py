import unittest
import database
import admin
import employee

class TestProyecto(unittest.TestCase):
    def test_modulos_cargados(self):
        # Verifica la carga e importación de la arquitectura del sistema
        self.assertIsNotNone(database)
        self.assertIsNotNone(admin)
        self.assertIsNotNone(employee)

if __name__ == '__main__':
    unittest.main()
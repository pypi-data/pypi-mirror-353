import unittest
from media import media, mediana, moda, varianza, desviacion_estandar

class TestEstadisticas(unittest.TestCase):
    def setUp(self):
        self.numeros = [2, 4, 4, 4, 5, 5, 7, 9]
        self.decimales = [1.5, 2.5, 2.5, 3.5, 4.5]
        self.vacia = []

    def test_media(self):
        self.assertEqual(media(self.numeros), 5.0)
        self.assertEqual(media(self.decimales), 2.9)
        self.assertEqual(media(self.vacia), 0)

    def test_mediana(self):
        self.assertEqual(mediana(self.numeros), 4.5)
        self.assertEqual(mediana(self.decimales), 2.5)
        self.assertEqual(mediana(self.vacia), 0)

    def test_moda(self):
        self.assertEqual(moda(self.numeros), 4)
        self.assertEqual(moda(self.decimales), 2.5)
        self.assertIsNone(moda(self.vacia))

    def test_varianza(self):
        self.assertAlmostEqual(varianza(self.numeros), 4.0, places=2)
        self.assertAlmostEqual(varianza(self.decimales), 1.24, places=2)
        self.assertEqual(varianza(self.vacia), 0)

    def test_desviacion_estandar(self):
        self.assertAlmostEqual(desviacion_estandar(self.numeros), 2.0, places=2)
        self.assertAlmostEqual(desviacion_estandar(self.decimales), 1.11, places=2)
        self.assertEqual(desviacion_estandar(self.vacia), 0)

if __name__ == '__main__':
    unittest.main()

import os
import unittest

from svgtag.shape2svg import shape_svg


class TestShape2SVG(unittest.TestCase):
    def test_shape_svg(self):
        # Définir le chemin de sortie pour le fichier SVG généré
        output_path = os.path.join(os.path.dirname(__file__), "outputs", "shape2svg")
        # Créer le répertoire s'il n'existe pas
        os.makedirs(output_path, exist_ok=True)

        width_mm = 80
        height_mm = 35
        thk = 1
        shape = "circle"
        phi = 5

        # Appeler shape_svg pour créer l'objet SVG
        svg = shape_svg(width_mm, height_mm, thk, shape, phi)

        # Définir les propriétés du SVG
        svg.unit = "mm"

        # Générer le fichier SVG
        svg_file_path = os.path.join(output_path, "shape.svg")
        svg.generate_svg_file(svg_file_path)

        # Vérifier que le fichier SVG a été créé
        self.assertTrue(os.path.exists(svg_file_path))


if __name__ == "__main__":
    unittest.main()

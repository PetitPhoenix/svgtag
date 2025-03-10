import os
import unittest

from SVGtag.SVGprocess import SVG, read_svg


class TestSVGprocess(unittest.TestCase):
    def setUp(self):
        # Définir le chemin de sortie pour les fichiers SVG générés
        self.output_path = os.path.join(
            os.path.dirname(__file__), "outputs", "SVGprocess"
        )
        # Créer le répertoire s'il n'existe pas
        os.makedirs(self.output_path, exist_ok=True)
        # Chemin vers le fichier SVG source
        self.source_svg_path = os.path.join(
            os.path.dirname(__file__), "..", "static", "images", "network.svg"
        )

    def test_read_and_generate_svg(self):
        # Lire le contenu SVG à partir d'un fichier
        svg_content = read_svg(self.source_svg_path)
        svg = SVG(svg_content)

        # Générer un fichier SVG et vérifier qu'il a été créé
        svg_file_path = os.path.join(self.output_path, "test_mm.svg")
        svg.generate_svg_file(svg_file_path)
        self.assertTrue(os.path.exists(svg_file_path))

        # Convertir les unités en pixels et générer un autre fichier SVG
        svg.convert_units("px")
        svg_file_path_px = os.path.join(self.output_path, "test_px.svg")
        svg.generate_svg_file(svg_file_path_px)
        self.assertTrue(os.path.exists(svg_file_path_px))

        # Ajouter un élément au SVG et générer un fichier SVG
        svg.add_element(
            "rect",
            {
                "x": "10",
                "y": "10",
                "width": "80",
                "height": "80",
                "stroke": "black",
                "fill": "transparent",
            },
            {"translate": (0, 0), "scale": 1},
        )
        svg_file_path_rect = os.path.join(self.output_path, "test_mm_rect.svg")
        svg.generate_svg_file(svg_file_path_rect)
        self.assertTrue(os.path.exists(svg_file_path_rect))


if __name__ == "__main__":
    unittest.main()

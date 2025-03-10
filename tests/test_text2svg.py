import os
import unittest

from SVGtag.text2svg import text_svg


class TestText2SVG(unittest.TestCase):
    def setUp(self):
        # Définir le chemin de sortie pour les fichiers SVG générés
        self.output_path = os.path.join(os.path.dirname(__file__), "outputs", "text2svg")
        # Créer le répertoire s'il n'existe pas
        os.makedirs(self.output_path, exist_ok=True)
        # Chemin vers le fichier de police
        self.font_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "static",
            "fonts",
            "Allison",
            "Allison-Regular.ttf",
        )

    def test_text_svg(self):
        # Paramètres du texte
        text = "Un long texte à diviser ou ajuster"
        font_size = None

        # Paramètres visuels [mm]
        zoneWidth_mm = 80
        zoneHeight_mm = 40
        x_mm = 20
        y_mm = 10
        interline_ratio = 0.6

        # Générer le fichier SVG
        svg_text = text_svg(
            text,
            self.font_path,
            font_size,
            zoneWidth_mm - x_mm,
            zoneHeight_mm - y_mm,
            x_mm,
            y_mm,
            interline_ratio=interline_ratio,
        )
        svg_text.unit = "mm"
        svg_text.width = zoneWidth_mm
        svg_text.height = zoneHeight_mm
        svg_text.viewBox = [0, 0, zoneWidth_mm, zoneHeight_mm]
        svg_text.update_svg_content()
        svg_text.add_element(
            "rect",
            {
                "x": x_mm,
                "y": y_mm,
                "width": zoneWidth_mm - x_mm,
                "height": zoneHeight_mm - y_mm,
                "stroke": "black",
                "fill": "transparent",
                "stroke-width": 0.1,
            },
            {"translate": (0, 0), "scale": 1},
        )

        # Générer le fichier SVG et vérifier qu'il a été créé
        svg_file_path = os.path.join(self.output_path, "text_rec.svg")
        svg_text.generate_svg_file(svg_file_path)
        self.assertTrue(os.path.exists(svg_file_path))


if __name__ == "__main__":
    unittest.main()

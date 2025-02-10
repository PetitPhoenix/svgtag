import os
import unittest
from SVGtag.generators.wifi import QR_gen

class TestQRCodeGeneration(unittest.TestCase):

    def setUp(self):
        self.network = 'MyNetwork'
        self.password = 'MyPassword'
        self.protocol = 'WPA/WPA2'
        self.hidden = 'true'
        self.width_mm = 100
        self.height_mm = 100
        self.padding_mm = 5
        self.text_elements = [
            {'text': 'Bienvenue', 'width': 2/3, 'height': 1/4, 'x': 0, 'y': 0, 'font': 'Southmore.ttf', 'fontsize': 30},
            {'text': 'Profitez du wifi', 'width': 2/3, 'height': 1/10, 'x': 0, 'y': 1/4, 'font': 'BillionDreams.ttf', 'fontsize': 20},
            {'text': 'Réseau', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 6/12, 'font': 'Stark.ttf', 'fontsize': 18},
            {'text': f'{self.network}', 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 7.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13},
            {'text': 'Mot de passe', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 9/12, 'font': 'Stark.ttf', 'fontsize': 18},
            {'text': f'{self.password}', 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 10.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13}

        ]
        self.output_path = os.path.join(os.path.dirname(__file__), 'outputs', 'generators', 'wifi')
        os.makedirs(self.output_path, exist_ok=True)
        self.filename = 'Commande_XYZ'
        self.static_files_path = os.path.join(os.path.dirname(__file__), '..', 'static')

    def test_qr_code_generation(self):
        svg_instance = QR_gen(
            self.network, self.password, self.protocol, self.hidden,
            self.text_elements, self.width_mm, self.height_mm, self.padding_mm,
            self.static_files_path
        )
        output_file = os.path.join(self.output_path, self.filename + '.svg')
        svg_instance.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

if __name__ == '__main__':
    unittest.main()
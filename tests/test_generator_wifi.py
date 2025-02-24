import os
import unittest
import trimesh
from SVGtag.generators.wifi import QR_gen
from SVGtag.generators.tag import tag, svg2stl

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

    # def test_01_qr_code_generation(self):
    #     svg_instance = QR_gen(
    #         self.network, self.password, self.protocol, self.hidden,
    #         self.text_elements, self.width_mm, self.height_mm, self.padding_mm,
    #         self.static_files_path
    #     )
    #     output_file = os.path.join(self.output_path, self.filename + '.svg')
    #     svg_instance.generate_svg_file(output_file)
    #     self.assertTrue(os.path.exists(output_file))
        
    def test_02_tag_3D_recto(self):
        self.font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'Impact', 'impact.ttf'))
        shape = tag("", self.font_path, 100, 100, 0, shape='rectangle', outline=False)
        shape.generate_svg_file(os.path.join(self.output_path, 'shape.svg'))

        face1 = QR_gen(
            self.network, self.password, self.protocol, self.hidden,
            self.text_elements, self.width_mm, self.height_mm, self.padding_mm,
            self.static_files_path
        )
        output_file = os.path.join(self.output_path, 'face1.svg')
        face1.generate_svg_file(output_file)
                
        scene = svg2stl(os.path.join(self.output_path, 'shape.svg'), thickness=3, output_path = self.output_path, 
                        side_A = os.path.join(self.output_path, 'face1.svg'), 
                        side_B = None, brand = None)
        with open(os.path.join(self.output_path, 'wifi.html'), "w") as file:
            file.write(trimesh.viewer.scene_to_html(scene))
        
        self.assertTrue(os.path.exists(os.path.join(self.output_path, 'mesh.stl')))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, 'side_A.stl')))

        
    # def test_03_tag_3D_recto_verso_brand(self):
    #     self.font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'Impact', 'impact.ttf'))
    #     shape = tag("", self.font_path, 100, 100, 0, shape='rectangle', outline=False)
    #     shape.generate_svg_file(os.path.join(self.output_path, 'shape.svg'))

    #     face1 = QR_gen(
    #         self.network, self.password, self.protocol, self.hidden,
    #         self.text_elements, self.width_mm, self.height_mm, self.padding_mm,
    #         self.static_files_path
    #     )
    #     output_file = os.path.join(self.output_path, 'face1.svg')
    #     face1.generate_svg_file(output_file)
        
    #     text2 = "Tetsudau"
    #     output_file = os.path.join(self.output_path, 'logo.svg')
    #     logo_font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'Allison', 'Allison-Regular.ttf'))
    #     svgtag = tag(text2, logo_font_path, 100, 100, 0, shape=None, outline=False)
    #     svgtag.generate_svg_file(output_file)
                
    #     scene = svg2stl(os.path.join(self.output_path, 'shape.svg'), thickness=3, output_path = self.output_path, 
    #                     side_A = os.path.join(self.output_path, 'face1.svg'), 
    #                     side_B = os.path.join(self.output_path, 'logo.svg'), brand = True)
    #     with open(os.path.join(self.output_path, 'wifi_brand.html'), "w") as file:
    #         file.write(trimesh.viewer.scene_to_html(scene))
        
    #     self.assertTrue(os.path.exists(os.path.join(self.output_path, 'mesh.stl')))
    #     self.assertTrue(os.path.exists(os.path.join(self.output_path, 'side_A.stl')))
    #     self.assertTrue(os.path.exists(os.path.join(self.output_path, 'side_B.stl')))

if __name__ == '__main__':
    unittest.main()
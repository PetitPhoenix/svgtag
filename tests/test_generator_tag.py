import os
import shutil
import unittest
from SVGtag.generators.tag import tag, tag_3D, tag_3D_RV

class TestTag(unittest.TestCase):
    def setUp(self):
        # Define the output path for the generated SVG files
        self.output_path = os.path.join(os.path.dirname(__file__), 'outputs', 'generators', 'tag')
        # Create the directory if it does not exist
        os.makedirs(self.output_path, exist_ok=True)
        # Define the input path for the SVG files used by tag_3D and tag_3D_RV
        self.input_path = self.output_path  # Assuming input files are in the same directory as output
        self.font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'Impact', 'impact.ttf'))

    def test_01_tag_shape_only(self):
        output_file = os.path.join(self.output_path, 'tag_shp.svg')
        svgtag = tag("", self.font_path, 80, 35, 0, shape='circle', outline=True)
        svgtag.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_01_tag_with_text1(self):
        text1 = "Impression d'une étiquette"
        output_file = os.path.join(self.output_path, 'tag1.svg')
        svgtag = tag(text1, self.font_path, 80, 35, 0, shape='circle', outline=True)
        svgtag.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_01_tag_with_text2(self):
        text2 = "Recto / Verso"
        output_file = os.path.join(self.output_path, 'tag2.svg')
        svgtag = tag(text2, self.font_path, 80, 35, 0, shape='circle', outline=True)
        svgtag.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_02_tag_text_only1(self):
        text1 = "Impression d'une étiquette"
        output_file = os.path.join(self.output_path, 'tag_txt1.svg')
        svgtag = tag(text1, self.font_path, 80, 35, 0, shape='circle', outline=False)
        svgtag.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_02_tag_text_only2(self):
        text2 = "Recto / Verso"
        output_file = os.path.join(self.output_path, 'tag_txt2.svg')
        svgtag = tag(text2, self.font_path, 80, 35, 0, shape='circle', outline=False)
        svgtag.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_03_tag_3D(self):
        filename = 'tag_txt1'
        self.input_path2 = os.path.join(os.path.dirname(__file__), 'inputs')
        shutil.copyfile(os.path.join(self.input_path2, 'shape_ink.svg'), os.path.join(self.output_path, 'shape.svg'))
        shutil.copyfile(os.path.join(self.input_path2, 'hole_ink.svg'), os.path.join(self.output_path, 'hole.svg'))
        shutil.copyfile(os.path.join(self.input_path2, 'Tetsudau_logo.svg'), os.path.join(self.output_path, 'Tetsudau_logo.svg'))
        tag_3D(filename, self.input_path, self.output_path)
        self.assertTrue(os.path.exists(os.path.join(self.output_path, '01_logo.stl')))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, f'{filename}_0.stl')))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, f'{filename}_1.stl')))

    def test_03_tag_3D_RV(self):
        recto = 'tag_txt1'
        verso = 'tag_txt2'
        tag_3D_RV(recto, verso, self.input_path, self.output_path)
        outputname = recto + '-' + verso.split("_", 1)[-1]
        self.assertTrue(os.path.exists(os.path.join(self.output_path, f'{outputname}_0.stl')))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, f'{recto}_1.stl')))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, f'{verso}_1.stl')))

if __name__ == '__main__':
    unittest.main()
import os
import unittest
from trimesh import viewer # if not written, error in import
from svgtag.generators.tag import tag_3D, tag
from svgtag.mesh import create_scene

class TestTag(unittest.TestCase):
    def setUp(self):
        # Define the output path for the generated SVG files
        self.output_path = os.path.join(
            os.path.dirname(__file__), "outputs", "generators", "tag"
        )
        # Create the directory if it does not exist
        os.makedirs(self.output_path, exist_ok=True)
        self.font_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "static", "fonts", "Impact", "impact.ttf"
            )
        )

    def test_01_tag_shape_only(self):
        output_file = os.path.join(self.output_path, "shape.svg")
        svgtag = tag("", self.font_path, 80, 35, 5, shape="circle", outline=False)
        svgtag.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_01_tag_shape_only_with_outline(self):
        # vérifier car pas outline
        output_file = os.path.join(self.output_path, "shape_outline.svg")
        svgtag = tag("", self.font_path, 80, 35, 5, shape="circle", outline=True)
        svgtag.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_01_tag_with_text1(self):
        text1 = "Impression d'une étiquette"
        output_file = os.path.join(self.output_path, "tag.svg")
        svgtag = tag(text1, self.font_path, 80, 35, 5, shape="circle", outline=True)
        svgtag.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_02_tag_text_only(self):
        text1 = "Impression d'une étiquette"
        output_file = os.path.join(self.output_path, "tag_txt.svg")
        svgtag = tag(text1, self.font_path, 80, 35, 0, shape=None, outline=False)
        svgtag.generate_svg_file(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_03_tag_3D_recto(self):
        shape = tag("", self.font_path, 80, 35, 5, shape="circle")

        text1 = "Impression d'une étiquette"
        recto = tag(text1, self.font_path, 80, 35)

        mesh, side_A_mesh, _ = tag_3D(
            [shape, recto], 
            thickness=3,
            brand=None,
            full_export=True
        )
        mesh.export(os.path.join(self.output_path, 'tag_3D_recto.stl'))
        side_A_mesh.export(os.path.join(self.output_path, 'tag_3D_recto_A.stl'))
        
        scene = create_scene([mesh, side_A_mesh])
        with open(os.path.join(self.output_path, 'tag_3D_recto.html'), "w") as file:
            file.write(viewer.scene_to_html(scene))

        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto_A.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto.html")))

    def test_04_tag_3D_recto_verso(self):
        shape = tag("", self.font_path, 80, 35, 5, shape="circle")

        text1 = "Impression d'une étiquette"
        recto = tag(text1, self.font_path, 80, 35, 0)

        text2 = "Recto / Verso"
        verso = tag(text2, self.font_path, 80, 35, 0)

        mesh, side_A_mesh, side_B_mesh = tag_3D(
            [shape, recto, verso], 
            thickness=3,
            brand=None,
            full_export=True
        )
        mesh.export(os.path.join(self.output_path, 'tag_3D_recto_verso.stl'))
        side_A_mesh.export(os.path.join(self.output_path, 'tag_3D_recto_verso_A.stl'))
        side_B_mesh.export(os.path.join(self.output_path, 'tag_3D_recto_verso_B.stl'))
        
        scene = create_scene([mesh, side_A_mesh])
        with open(os.path.join(self.output_path, 'tag_3D_recto_verso.html'), "w") as file:
            file.write(viewer.scene_to_html(scene))

        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto_verso.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto_verso_A.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto_verso_B.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto_verso.html")))


    def test_05_tag_3D_recto_verso_brand(self):
        shape = tag("", self.font_path, 80, 35, 5, shape="circle", outline=False)

        text1 = "Impression d'une étiquette"
        recto = tag(text1, self.font_path, 80, 35, 0, shape=None, outline=False)

        text2 = "Tetsudau"
        logo_font_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "static",
                "fonts",
                "Allison",
                "Allison-Regular.ttf",
            )
        )
        verso = tag(text2, logo_font_path, 80, 35, 0, shape=None, outline=False)

        mesh, side_A_mesh, side_B_mesh = tag_3D(
            [shape, recto, verso], 
            thickness=3,
            brand=True,
            full_export=True
        )
        mesh.export(os.path.join(self.output_path, 'tag_3D_recto_verso_brand.stl'))
        side_A_mesh.export(os.path.join(self.output_path, 'tag_3D_recto_verso_brand_A_mesh.stl'))
        side_B_mesh.export(os.path.join(self.output_path, 'tag_3D_recto_verso_brand_B.stl'))
        
        scene = create_scene([mesh, side_A_mesh])
        with open(os.path.join(self.output_path, 'tag_3D_recto_verso_brand.html'), "w") as file:
            file.write(viewer.scene_to_html(scene))

        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto_verso_brand.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto_verso_brand_A_mesh.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto_verso_brand_B.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "tag_3D_recto_verso_brand.html")))


if __name__ == "__main__":
    unittest.main()

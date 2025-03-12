import os
import unittest
from trimesh import viewer # if not written, error in import
from svgtag.generators.tag import svg2stl, tag


class TestTag(unittest.TestCase):
    def setUp(self):
        # Define the output path for the generated SVG files
        self.output_path = os.path.join(
            os.path.dirname(__file__), "outputs", "generators", "tag"
        )
        # Create the directory if it does not exist
        os.makedirs(self.output_path, exist_ok=True)
        # Define the input path for the SVG files used by tag_3D and tag_3D_RV
        self.input_path = (
            self.output_path
        )  # Assuming input files are in the same directory as output
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
        shape = tag("", self.font_path, 80, 35, 5, shape="circle", outline=False)
        shape.generate_svg_file(os.path.join(self.output_path, "shape.svg"))

        text1 = "Impression d'une étiquette"
        output_file = os.path.join(self.output_path, "tag_txt.svg")
        svgtag = tag(text1, self.font_path, 80, 35, 0, shape=None, outline=False)
        svgtag.generate_svg_file(output_file)

        scene = svg2stl(
            os.path.join(self.output_path, "shape.svg"),
            thickness=3,
            output_path=self.output_path,
            side_A=os.path.join(self.output_path, "tag_txt.svg"),
            side_B=None,
            brand=None,
        )
        with open(os.path.join(self.output_path, "tag_3D_recto.html"), "w") as file:
            file.write(viewer.scene_to_html(scene))

        self.assertTrue(os.path.exists(os.path.join(self.output_path, "mesh.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "side_A.stl")))

    def test_03_tag_3D_recto_verso(self):
        shape = tag("", self.font_path, 80, 35, 5, shape="circle", outline=False)
        shape.generate_svg_file(os.path.join(self.output_path, "shape.svg"))

        text1 = "Impression d'une étiquette"
        output_file = os.path.join(self.output_path, "tag_txt_R.svg")
        svgtag = tag(text1, self.font_path, 80, 35, 0, shape=None, outline=False)
        svgtag.generate_svg_file(output_file)

        text2 = "Recto / Verso"
        output_file = os.path.join(self.output_path, "tag_txt_V.svg")
        svgtag = tag(text2, self.font_path, 80, 35, 0, shape=None, outline=False)
        svgtag.generate_svg_file(output_file)

        scene = svg2stl(
            os.path.join(self.output_path, "shape.svg"),
            thickness=3,
            output_path=self.output_path,
            side_A=os.path.join(self.output_path, "tag_txt_R.svg"),
            side_B=os.path.join(self.output_path, "tag_txt_V.svg"),
            brand=None,
        )
        with open(os.path.join(self.output_path, "tag_3D_recto_verso.html"), "w") as file:
            file.write(viewer.scene_to_html(scene))

        self.assertTrue(os.path.exists(os.path.join(self.output_path, "mesh.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "side_A.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "side_B.stl")))

    def test_03_tag_3D_recto_verso_brand(self):
        shape = tag("", self.font_path, 80, 35, 5, shape="circle", outline=False)
        shape.generate_svg_file(os.path.join(self.output_path, "shape.svg"))

        text1 = "Impression d'une étiquette"
        output_file = os.path.join(self.output_path, "tag_txt_R.svg")
        svgtag = tag(text1, self.font_path, 80, 35, 0, shape=None, outline=False)
        svgtag.generate_svg_file(output_file)

        text2 = "Tetsudau"
        output_file = os.path.join(self.output_path, "logo.svg")
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
        svgtag = tag(text2, logo_font_path, 80, 35, 0, shape=None, outline=False)
        svgtag.generate_svg_file(output_file)

        scene = svg2stl(
            os.path.join(self.output_path, "shape.svg"),
            thickness=3,
            output_path=self.output_path,
            side_A=os.path.join(self.output_path, "tag_txt_R.svg"),
            side_B=os.path.join(self.output_path, "logo.svg"),
            brand=True,
        )
        with open(
            os.path.join(self.output_path, "tag_3D_recto_verso_brand.html"), "w"
        ) as file:
            file.write(viewer.scene_to_html(scene))

        self.assertTrue(os.path.exists(os.path.join(self.output_path, "mesh.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "side_A.stl")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path, "side_B.stl")))


if __name__ == "__main__":
    unittest.main()

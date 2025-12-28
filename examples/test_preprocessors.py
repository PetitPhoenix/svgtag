"""
Test des preprocessors SVG
Génère Face A et Face B avec leurs shapes pour visualiser les transformations
"""
from pathlib import Path
from svgtag.svg.shapes import tag_circle_svg
from svgtag.svg.composition import add_text_zone
from svgtag.svg.base import SVG

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / "test_preprocessors"
output_path.mkdir(parents=True, exist_ok=True)

font_path = str(ROOT / "static" / "fonts" / "Impact" / "impact.ttf")

svg, layout = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)
area = layout.get_area('main')
add_text_zone(svg, "Test Face A", font_path, area, n=1)
svg.generate_svg_file(str(output_path / "face_A.svg"))

svg_H = svg.flip('horizontal')
svg_H.generate_svg_file(str(output_path / "face_A_H.svg"))

svg_V= svg.flip('vertical')
svg_V.generate_svg_file(str(output_path / "face_A_V.svg"))